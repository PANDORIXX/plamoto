from flask import Flask, render_template, redirect, url_for, request, jsonify, flash
from camera import capture_image, picam_unavailability_logging, Picamera2
from settings import load_settings, save_settings, get_interval_minutes_from_settings, parse_form_settings
from config import Config
from logger import setup_logger
from background_capture import start_background_thread, stop_background_thread, compute_next_in_minutes
from external_access import start_cloudflare_quick_tunnel
import os
from extensions import db
from flask_migrate import Migrate

# -------------------------------
# Logging setup
# -------------------------------
logger = setup_logger(__name__)

# Logging when Picamera2 is not available
if Picamera2 is None: 
    picam_unavailability_logging()

# -------------------------------
# Flask app
# -------------------------------
app = Flask(__name__)

# Load configuration constants
app.config.from_object(Config)

# Load settings once at startup and set secret key
app.config['SETTINGS'] = load_settings(app.config['SETTINGS_FILE'])
app.secret_key = app.config['SECRET_KEY']

# PostgreSQL Database setup
db.init_app(app)
migrate = Migrate(app, db)

from models import Plant

# -------------------------------
# Routes
# -------------------------------
@app.route('/')
def index():
    images = sorted(os.listdir(app.config['IMAGE_DIR']), reverse=True)
    latest_image = images[0] if images else None

    next_in_min = compute_next_in_minutes()
    background_active = next_in_min is not None

    return render_template(
        'dashboard.html',
        active_page='dashboard',
        latest_image=latest_image,
        background_capture_active=background_active,
        background_capture_next_in=next_in_min
    )

@app.route('/capture')
def capture():
    capture_image(app.config['SETTINGS'])
    return redirect(url_for('index'))

@app.route('/toggle_background_capture', methods=['POST'])
def toggle_background_capture():
    if compute_next_in_minutes() is not None:
        stop_background_thread()
        active = False
        next_in = None
    else:
        interval_min = get_interval_minutes_from_settings(app.config['SETTINGS'])
        start_background_thread(lambda: app.config['SETTINGS'], interval_minutes=interval_min)
        active = True
        next_in = interval_min
    return jsonify({'active': active, 'next_in': next_in})

@app.route('/background_capture_status')
def background_capture_status():
    next_in_min = compute_next_in_minutes()
    return jsonify({
        'active': next_in_min is not None,
        'next_in': next_in_min
    })

@app.route('/latest_image')
def latest_image():
    """Return the URL of the latest captured image."""
    images = sorted(os.listdir(app.config['IMAGE_DIR']), reverse=True)
    latest = images[0] if images else None
    url = url_for('static', filename=f'images/{latest}') if latest else ''
    return jsonify({'url': url})

@app.route('/plants')
def plants():
    all_plants = Plant.query.order_by(Plant.created_at.desc()).all()
    return render_template('plants.html', active_page='plants', plants=all_plants)

@app.route('/add_plant', methods=['GET', 'POST'])
def add_plant():
    if request.method == 'POST':
        # Process form submission
        name = request.form.get('name')
        location = request.form.get('location')

        if not name:
            flash("Plant name is required!", "error")
            return redirect(url_for('add_plant'))

        # Save new plant to database
        new_plant = Plant(name=name, location=location)
        db.session.add(new_plant)
        db.session.commit()

        flash(f"Plant '{name}' added successfully!", "success")
        return redirect(url_for('plants'))

    # GET: Show form
    return render_template(
        'plant_details.html',
        active_page='plants',
        plant=None,
        form_action=url_for('add_plant')
    )

@app.route('/edit_plant/<int:plant_id>', methods=['GET', 'POST'])
def edit_plant(plant_id):
    plant = Plant.query.get_or_404(plant_id)

    if request.method == 'POST':
        # Process form submission
        name = request.form.get('name')
        location = request.form.get('location')

        if not name:
            flash("Plant name is required!", "error")
            return redirect(url_for('edit_plant', plant_id=plant_id))

        # Update plant details
        plant.name = name
        plant.location = location
        db.session.commit()

        flash(f"Plant '{name}' updated successfully!", "success")
        return redirect(url_for('plants'))

    # GET: Show form with current plant details
    return render_template(
        'plant_details.html',
        active_page='plants',
        plant=plant,
        form_action=url_for('edit_plant', plant_id=plant.id)
    )

@app.route('/delete_plant/<int:plant_id>', methods=['POST'])
def delete_plant(plant_id):
    plant = Plant.query.get_or_404(plant_id)
    db.session.delete(plant)
    db.session.commit()
    flash(f"Plant '{plant.name}' deleted successfully!", "success")
    return redirect(url_for('plants'))

@app.route('/gallery')
def gallery():
    images = sorted(os.listdir(app.config['IMAGE_DIR']), reverse=True)
    return render_template('gallery.html', active_page='gallery', images=images)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        new_settings = parse_form_settings(request.form)

        save_settings(app.config['SETTINGS_FILE'], new_settings)
        app.config['SETTINGS'] = new_settings
        logger.info('Settings saved and applied.')

        # If thread is running, update its schedule
        next_in_min = compute_next_in_minutes()
        if next_in_min is not None:
            interval_min = get_interval_minutes_from_settings(app.config['SETTINGS'])
            # restart with new interval
            start_background_thread(
                settings_getter=lambda: app.config['SETTINGS'],
                interval_minutes=interval_min
            )

        return redirect(url_for('settings'))

    # GET: load settings for form
    current_settings = load_settings(app.config['SETTINGS_FILE'])
    return render_template('settings.html', **current_settings, active_page='settings')

# -------------------------------
# Main
# -------------------------------
if __name__ == '__main__':
    # Start Cloudflare Quick Tunnel for external network access
    # start_cloudflare_quick_tunnel()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])