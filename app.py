from flask import Flask, render_template, redirect, url_for, request, jsonify
from camera import capture_image, picam_unavailability_logging, Picamera2
from settings import load_settings, save_settings, get_interval_minutes_from_settings
from config import Config
from logging import setup_logger
from background_capture import start_background_thread, stop_background_thread, compute_next_in_minutes
import threading
import os
import time
import subprocess
import re
import shutil

# -------------------------------
# Logging setup
# -------------------------------
logger = setup_logger(__name__)

# Logging when Picamera2 is not available
if Picamera2 is None: 
    picam_unavailability_logging()

# -------------------------------
# Cloudflare setup
# -------------------------------
def start_cloudflare_quick_tunnel(max_wait_sec=15):
    """
    Start a Cloudflare Quick Tunnel in a daemon thread.
    Logs the public URL if successful, otherwise logs an error and raises RuntimeError.
    """

    # Check if cloudflared is installed
    if not shutil.which("cloudflared"):
        logger.error("cloudflared is not installed. Please install it first.")
        raise RuntimeError("cloudflared is not installed. Please install it first.")

    tunnel_info = {"url": None, "error": None}

    def run_tunnel():
        try:
            process = subprocess.Popen(
                ["cloudflared", "tunnel", "--url", "http://localhost:5000"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            for line in process.stdout:
                line = line.strip()
                # Extract trycloudflare.com URL
                match = re.search(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", line)
                if match:
                    tunnel_info["url"] = match.group(0)
                    break

            if not tunnel_info["url"]:
                # Read stderr as fallback for errors
                tunnel_info["error"] = process.stderr.read().strip()

            # Keep process running in background
            process.wait()
        except Exception as e:
            tunnel_info["error"] = str(e)

    # Run in daemon thread
    thread = threading.Thread(target=run_tunnel, daemon=True)
    thread.start()

    # Wait a short time for URL to appear
    start_time = time.time()
    while time.time() - start_time < max_wait_sec:
        if tunnel_info["url"]:
            logger.info(f"Your app is publicly reachable at: {tunnel_info['url']}")
            return tunnel_info["url"]
        if tunnel_info["error"]:
            logger.error(f"Cloudflare Tunnel failed: {tunnel_info['error']}")
            raise RuntimeError(f"Cloudflare Tunnel failed: {tunnel_info['error']}")
        time.sleep(0.2)

    # Timeout
    logger.error("Cloudflare Tunnel did not start in time or no URL was returned.")
    raise RuntimeError("Cloudflare Tunnel did not start in time or no URL was returned.")

# -------------------------------
# Flask app
# -------------------------------
app = Flask(__name__)

# Load configuration constants
app.config.from_object(Config)

# Load settings once at startup
app.config['SETTINGS'] = load_settings(app.config['SETTINGS_FILE'])

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

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        # Read values from form (strings by default)
        background_capture_interval = request.form.get('background_capture_interval')
        camera_source = request.form.get('camera_source')
        droidcam_ip = request.form.get('droidcam_ip')
        droidcam_port = request.form.get('droidcam_port')
        picam_awb_mode = request.form.get('picam_awb_mode')

        # Sanitize interval (minutes)
        try:
            background_capture_interval = max(1, int(background_capture_interval))
        except (ValueError, TypeError):
            background_capture_interval = get_interval_minutes_from_settings(app.config['SETTINGS'])

        new_settings = {
            'background_capture_interval': int(background_capture_interval),
            'camera_source': camera_source,
            'droidcam_ip': droidcam_ip,
            'droidcam_port': int(droidcam_port),
            'picam_awb_mode': int(picam_awb_mode)
        }

        save_settings(app.config['SETTINGS_FILE'], new_settings)
        app.config['SETTINGS'] = new_settings
        logger.info('Settings saved and applied.')

        # If thread is running, update its schedule.
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

# -------------------------------
# Main
# -------------------------------
if __name__ == '__main__':
    # Start Cloudflare Quick Tunnel
    start_cloudflare_quick_tunnel()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000)