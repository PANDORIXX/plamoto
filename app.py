from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template, redirect, url_for, request, jsonify, flash
from camera import capture_image, picam_unavailability_logging, Picamera2
from settings import load_settings, save_settings, get_interval_minutes_from_settings, parse_form_settings
from config import Config
from logger import setup_logger
from background_capture import start_background_thread, stop_background_thread, compute_next_in_minutes
from external_access import start_cloudflare_quick_tunnel
from extensions import db
from flask_migrate import Migrate
from models import Plant
import os
import threading

# -------------------------------
# Logging setup
# -------------------------------
logger = setup_logger(__name__)
if Picamera2 is None:
    picam_unavailability_logging()

# -------------------------------
# Flask app setup
# -------------------------------
app = Flask(__name__)
app.config.from_object(Config)

# Load settings safely
try:
    app.config['SETTINGS'] = load_settings(app.config['SETTINGS_FILE'])
except Exception as e:
    logger.exception("Failed to load settings. Using empty defaults.")
    app.config['SETTINGS'] = {}

app.secret_key = app.config.get('SECRET_KEY', os.urandom(32))

# Database setup
db.init_app(app)
Migrate(app, db)

# Lock to prevent race conditions in background capture
background_lock = threading.Lock()

# -------------------------------
# Helper functions
# -------------------------------
# --- Database ---
def safe_commit():
    """Commit DB session safely."""
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.exception("Database commit failed")
        flash("Database error occurred.", "error")

# --- Image handling ---
def get_all_images():
    """Return sorted list of all images, newest first."""
    try:
        return sorted(os.listdir(app.config['IMAGE_DIR']), reverse=True)
    except Exception as e:
        logger.exception("Failed to list images")
        return []

def get_latest_image():
    images = get_all_images()
    return images[0] if images else None

def get_latest_image_url():
    latest = get_latest_image()
    if latest:
        return url_for('static', filename=f'images/{latest}')
    return ''

def remove_image(filename):
    file_path = os.path.join(app.root_path, 'static', filename)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            flash(f"Image '{os.path.basename(filename)}' deleted successfully!", "success")
        else:
            flash(f"Image '{os.path.basename(filename)}' not found!", "error")
    except Exception as e:
        logger.exception("Failed to remove image")
        flash("Failed to delete image.", "error")

# --- Background capture handling ---
def update_background_capture(start=None, interval=None):
    """
    Manage background capture thread safely.
    - start=True: force start
    - start=False: force stop
    - interval: new interval in minutes (only applies if thread is running)
    Returns: dict with {'active': bool, 'next_in': int or None}
    """
    with background_lock:
        try:
            currently_active = compute_next_in_minutes() is not None

            # Stop thread if explicitly requested
            if start is False:
                stop_background_thread()
                return {'active': False, 'next_in': None}

            # Update interval if requested and thread is active
            if interval is not None and currently_active:
                stop_background_thread()
                start_background_thread(lambda: app.config['SETTINGS'], interval_minutes=interval)
                return {'active': True, 'next_in': interval}

            # Start thread if requested and currently inactive
            if start is True and not currently_active:
                if interval is None:
                    interval = get_interval_minutes_from_settings(app.config['SETTINGS'])
                start_background_thread(lambda: app.config['SETTINGS'], interval_minutes=interval)
                return {'active': True, 'next_in': interval}

            # Return current status if no action
            return {'active': currently_active, 'next_in': compute_next_in_minutes()}

        except Exception as e:
            logger.exception("Failed to update background capture")
            return {'active': False, 'next_in': None, 'error': str(e)}

# --- Plant handling ---
def save_plant(plant, name, location):
    if not name:
        flash("Plant name is required!", "error")
        return False
    plant.name = name
    plant.location = location
    db.session.add(plant)
    safe_commit()
    return True

# -------------------------------
# Routes
# -------------------------------
# --- Dashboard ---
@app.route('/')
def index():
    return render_template(
        'dashboard.html',
        active_page='dashboard',
        latest_image=get_latest_image_url(),
        background_capture_active=compute_next_in_minutes() is not None,
        background_capture_next_in=compute_next_in_minutes()
    )

@app.route('/capture')
def capture():
    try:
        capture_image(app.config['SETTINGS'])
        flash("Image captured successfully!", "success")
    except Exception as e:
        logger.exception("Image capture failed")
        flash("Failed to capture image.", "error")
    return redirect(url_for('index'))

@app.route('/toggle_background_capture', methods=['POST'])
def toggle_background_capture():
    currently_active = compute_next_in_minutes() is not None
    new_status = update_background_capture(start=not currently_active)
    logger.info(f"Background capture toggled: {new_status}")
    return jsonify(new_status)

@app.route('/background_capture_status')
def background_capture_status():
    next_in = compute_next_in_minutes()
    return jsonify({'active': next_in is not None, 'next_in': next_in})

@app.route('/latest_image')
def latest_image():
    return jsonify({'url': get_latest_image_url()})

# --- Gallery ---
@app.route('/gallery')
def gallery():
    return render_template('gallery.html', active_page='gallery', images=get_all_images())

@app.route('/remove_picture/<path:filename>', methods=['POST'])
def remove_picture(filename):
    remove_image(filename)
    return redirect(url_for('gallery'))

# --- Plants ---
@app.route('/plants')
def plants():
    try:
        all_plants = Plant.query.order_by(Plant.created_at.desc()).all()
        return render_template('plants.html', active_page='plants', plants=all_plants)
    except Exception as e:
        logger.exception("Failed to load plants")
        flash("Failed to load plants.", "error")
        return redirect(url_for('index'))

@app.route('/add_plant', methods=['GET', 'POST'])
def add_plant():
    if request.method == 'POST':
        name = request.form.get('name')
        location = request.form.get('location')
        if save_plant(Plant(), name, location):
            flash(f"Plant '{name}' added successfully!", "success")
            logger.info(f"New plant added: {name}")
            return redirect(url_for('plants'))
        return redirect(url_for('add_plant'))
    return render_template('plant_details.html', active_page='plants', plant=None, form_action=url_for('add_plant'))

@app.route('/edit_plant/<int:plant_id>', methods=['GET', 'POST'])
def edit_plant(plant_id):
    plant = Plant.query.get_or_404(plant_id)
    if request.method == 'POST':
        name = request.form.get('name')
        location = request.form.get('location')
        if save_plant(plant, name, location):
            flash(f"Plant '{name}' updated successfully!", "success")
            logger.info(f"Plant updated: {name}")
            return redirect(url_for('plants'))
        return redirect(url_for('edit_plant', plant_id=plant_id))
    return render_template('plant_details.html', active_page='plants', plant=plant, form_action=url_for('edit_plant', plant_id=plant.id))

@app.route('/delete_plant/<int:plant_id>', methods=['POST'])
def delete_plant(plant_id):
    plant = Plant.query.get_or_404(plant_id)
    db.session.delete(plant)
    safe_commit()
    flash(f"Plant '{plant.name}' deleted successfully!", "success")
    logger.info(f"Plant deleted: {plant.name}")
    return redirect(url_for('plants'))

# --- Settings ---
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        try:
            new_settings = parse_form_settings(request.form, app.config['SETTINGS'])
            save_settings(app.config['SETTINGS_FILE'], new_settings)
            app.config['SETTINGS'] = new_settings
            logger.info('Settings saved and applied.')

            # Update background capture interval if active
            if compute_next_in_minutes() is not None:
                update_background_capture(start=None, interval=get_interval_minutes_from_settings(new_settings))
            flash("Settings saved successfully.", "success")
        except Exception as e:
            logger.exception("Failed to save settings")
            flash("Failed to save settings.", "error")
        return redirect(url_for('settings'))

    current_settings = load_settings(app.config['SETTINGS_FILE'])
    return render_template('settings.html', **current_settings, active_page='settings')

# -------------------------------
# Main
# -------------------------------
if __name__ == '__main__':
    try:
        if app.config.get('CLOUDFLARE_ENABLED', False):
            start_cloudflare_quick_tunnel()
    except Exception as e:
        logger.exception("Failed to start Cloudflare Quick Tunnel")
    
    app.run(host='0.0.0.0', port=5000, debug=app.config.get('DEBUG', False))
