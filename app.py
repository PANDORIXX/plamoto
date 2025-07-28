from flask import Flask, render_template, redirect, url_for, request
from camera import droidcam_capture_image, picam_capture_image
import threading
import logging
from logging.handlers import RotatingFileHandler
import os
import time
import json

SETTINGS_FILE = 'settings.json'
IMAGE_DIR = 'static/images'
LOG_FILE = 'logs/plant_monitor.log'
BACKGROUND_CAPTURE_INTERVAL = 60 * 60

# Function to load current settings out of json
def load_settings():
    try:
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'camera_source': 'droidcam'}

# Function to save changes to the settings to json
def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)

# Function to capture image according the currently selected camera source
def capture_image():
    settings = app.config['SETTINGS']
    if settings.get('camera_source') == 'droidcam':
        droidcam_capture_image()
    else:
        picam_capture_image()

# Background thread for capturing images at regular intervals
class BackgroundCaptureThread(threading.Thread):
    def __init__(self, interval=BACKGROUND_CAPTURE_INTERVAL):
        super().__init__()
        self.interval = interval
        self._stop_event = threading.Event()
        self.next_capture_time = None
        self.is_running = False

    def run(self):
        self.is_running = True
        while not self._stop_event.is_set():
            self.next_capture_time = time.time() + self.interval
            capture_image()
            time.sleep(self.interval)

    def stop(self):
        self._stop_event.set()

# Create logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create RotatingFileHandler with formatter
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=1024*1024, backupCount=2)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Create StreamHandler (console)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Flask application to serve the camera images and capture new images
app = Flask(__name__)

# Initialize app config
app.config['SETTINGS'] = load_settings()
app.config['BACKGROUND_CAPTURE_THREAD'] = None

# Landing page with latest image
@app.route('/')
def index():
    images = sorted(os.listdir(IMAGE_DIR), reverse=True)
    latest_image = images[0] if images else None
    if app.config['BACKGROUND_CAPTURE_THREAD'] and app.config['BACKGROUND_CAPTURE_THREAD'].is_running:
        background_capture_next_in = int(max(0, app.config['BACKGROUND_CAPTURE_THREAD'].next_capture_time - time.time())/60)
        return render_template('index.html', latest_image=latest_image, background_capture_active=True, background_capture_next_in=background_capture_next_in)
    else:
        return render_template('index.html', latest_image=latest_image, background_capture_active=False, background_capture_next_in=None)


# Link to settings page
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        # Read values from form
        camera_source = request.form.get('camera_source')
        picam_resolution = request.form.get('picam_resolution', '1280x720')

        # Save to settings file
        new_settings = {
            'camera_source': camera_source,
            'picam_resolution': picam_resolution
        }
        save_settings(new_settings)
        app.config['SETTINGS'] = new_settings

        return redirect(url_for('settings'))  # Reload page with new values

    # For GET request – load settings to show in form
    current_settings = load_settings()
    return render_template('settings.html', **current_settings)

# Link to capture a new image
@app.route('/capture')
def capture():
    capture_image()
    return redirect(url_for('index'))

# Link to toggle background capture
@app.route('/toggle_background_capture')
def toggle_background_capture():
    if app.config['BACKGROUND_CAPTURE_THREAD'] and app.config['BACKGROUND_CAPTURE_THREAD'].is_alive():
        logging.info('Stopping background capture thread.')
        app.config['BACKGROUND_CAPTURE_THREAD'].stop()
        app.config['BACKGROUND_CAPTURE_THREAD'] = None
    else:
        logging.info('Starting background capture thread.')
        app.config['BACKGROUND_CAPTURE_THREAD'] = BackgroundCaptureThread()
        app.config['BACKGROUND_CAPTURE_THREAD'].start()
    time.sleep(2)
    return redirect(url_for('index'))

# Main
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)