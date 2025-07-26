from flask import Flask, render_template, redirect, url_for
from camera import capture_image
import threading
import logging
from logging.handlers import RotatingFileHandler
import os
import time

# Create logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create RotatingFileHandler with formatter
file_handler = RotatingFileHandler('logs/plant_monitor.log', maxBytes=1024*1024, backupCount=2)
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

# Background thread for capturing images at regular intervals
class BackgroundCaptureThread(threading.Thread):
    def __init__(self, interval=60*60):
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

# Landing page with latest image
@app.route('/')
def index():
    image_dir = 'static/images'
    images = sorted(os.listdir(image_dir), reverse=True)
    latest_image = images[0] if images else None
    if background_capture_thread and background_capture_thread.is_running:
        background_capture_next_in = int(max(0, background_capture_thread.next_capture_time - time.time())/60)
        return render_template('index.html', latest_image=latest_image, background_capture_active=True, background_capture_next_in=background_capture_next_in)
    else:
        return render_template('index.html', latest_image=latest_image, background_capture_active=False, background_capture_next_in=None)

# Link to capture a new image
@app.route('/capture')
def capture():
    capture_image()
    return redirect(url_for('index'))

# Link to toggle background capture
@app.route('/toggle_background_capture')
def toggle_background_capture():
    global background_capture_thread
    if background_capture_thread and background_capture_thread.is_alive():
        logging.info("Stopping background capture thread.")
        background_capture_thread.stop()
        background_capture_thread = None
    else:
        logging.info("Starting background capture thread.")
        background_capture_thread = BackgroundCaptureThread()
        background_capture_thread.start()
    time.sleep(2)
    return redirect(url_for('index'))
        
# Initialize variables
background_capture_thread = None

# Main
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)