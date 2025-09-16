from flask import Flask, render_template, redirect, url_for, request, jsonify
from camera import capture_image, picam_unavailability_logging, Picamera2
from settings import load_settings, save_settings
import threading
import os
import time
import subprocess
import re
import shutil
from config import Config
from logger_setup import setup_logger

# -------------------------------
# Background capture thread
# -------------------------------
class BackgroundCaptureThread(threading.Thread):
    """Thread that schedules background captures at a fixed minute interval."""

    def __init__(self, interval_minutes: int):
        super().__init__(daemon=True)
        self.interval_min = max(1, int(interval_minutes))  # safety: >= 1 minute
        self.interval_s = self.interval_min * 60
        self._stop_event = threading.Event()
        self.next_capture_time = None  # epoch seconds of next scheduled capture
        self.is_running = False

    def run(self):
        self.is_running = True

        try:
            # Capture immediately
            capture_image(app.config['SETTINGS'])

            # Shedule next capture
            now = time.time()
            self.next_capture_time = now + self.interval_s

            while not self._stop_event.is_set():
                # Sleep until it's time to capture (supports precise countdown)
                sleep_s = max(0.0, self.next_capture_time - time.time())
                # Sleep in small chunks to be responsive to stop()
                end_time = time.time() + sleep_s
                while not self._stop_event.is_set() and time.time() < end_time:
                    time.sleep(min(0.5, end_time - time.time()))

                if self._stop_event.is_set():
                    break

                # Perform capture
                capture_image(app.config['SETTINGS'])

                # Schedule next
                self.next_capture_time = time.time() + self.interval_s
        finally:
            self.is_running = False
            # Leave next_capture_time as-is for last known schedule, or set None
            # self.next_capture_time = None

    def stop(self):
        """Signal the thread to stop and return immediately."""
        self._stop_event.set()

    def reset_schedule_now(self):
        """Reschedule next capture from 'now' (used after saving settings)."""
        self.next_capture_time = time.time() + self.interval_s

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
app.config['BACKGROUND_CAPTURE_THREAD'] = None

# -------------------------------
# Logging setup
# -------------------------------
logger = setup_logger(__name__)

# Logging when Picamera2 is not available
if Picamera2 is None: 
    picam_unavailability_logging()

# -------------------------------
# Helpers
# -------------------------------
def get_interval_minutes_from_settings(settings: dict) -> int:
    """Parse interval minutes from settings; fallback to 60 if missing/invalid."""
    val = settings.get('background_capture_interval', 60)
    try:
        return max(1, int(val))
    except (ValueError, TypeError):
        return 60


def start_background_thread():
    """Start background capture thread using current settings."""
    stop_background_thread(join=True)
    interval_min = get_interval_minutes_from_settings(app.config['SETTINGS'])
    t = BackgroundCaptureThread(interval_minutes=interval_min)
    t.start()
    app.config['BACKGROUND_CAPTURE_THREAD'] = t
    logger.info(f"Background capture thread started (interval={interval_min} min).")


def stop_background_thread(join: bool = True):
    """Stop background capture thread if running."""
    t = app.config.get('BACKGROUND_CAPTURE_THREAD')
    if t and t.is_alive():
        logger.info("Stopping background capture thread…")
        t.stop()
        if join:
            t.join(timeout=5.0)
        logger.info("Background capture thread stopped.")
    app.config['BACKGROUND_CAPTURE_THREAD'] = None


def compute_next_in_minutes(thread: BackgroundCaptureThread):
    """Return remaining minutes (int) until next capture, or None if unknown."""
    if not thread or not thread.is_running:
        return None
    nxt = thread.next_capture_time
    if not nxt:
        return None
    seconds_left = max(0, nxt - time.time())
    return int(seconds_left // 60)


# -------------------------------
# Routes
# -------------------------------
@app.route('/')
def index():
    images = sorted(os.listdir(app.config['IMAGE_DIR']), reverse=True)
    latest_image = images[0] if images else None

    thread = app.config.get('BACKGROUND_CAPTURE_THREAD')
    if thread and thread.is_running:
        next_in_min = compute_next_in_minutes(thread)
        return render_template(
            'dashboard.html',
            active_page='dashboard',
            latest_image=latest_image,
            background_capture_active=True,
            background_capture_next_in=next_in_min
        )
    else:
        return render_template(
            'dashboard.html',
            active_page='dashboard',
            latest_image=latest_image,
            background_capture_active=False,
            background_capture_next_in=None
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
            'background_capture_interval': background_capture_interval,
            'camera_source': camera_source,
            'droidcam_ip': droidcam_ip,
            'droidcam_port': droidcam_port,
            'picam_awb_mode': picam_awb_mode
        }

        save_settings(app.config['SETTINGS_FILE'], new_settings)
        app.config['SETTINGS'] = new_settings
        logger.info('Settings saved and applied.')

        # If thread is running, update its schedule.
        thread = app.config.get('BACKGROUND_CAPTURE_THREAD')
        if thread and thread.is_running:
            # If interval changed, restart the thread to apply new interval.
            if thread.interval_min != background_capture_interval:
                logger.info("Interval changed; restarting background capture thread with new interval.")
                start_background_thread()
            else:
                # Only reschedule to prevent '0 minutes' display right after saving.
                logger.info("Interval unchanged; resetting next capture schedule.")
                thread.reset_schedule_now()

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
    thread = app.config.get('BACKGROUND_CAPTURE_THREAD')
    if thread and thread.is_alive() and thread.is_running:
        stop_background_thread()
        active = False
        next_in = None
    else:
        start_background_thread()
        active = True
        next_in = get_interval_minutes_from_settings(app.config['SETTINGS'])

    return jsonify({'active': active, 'next_in': next_in})


@app.route('/background_capture_status')
def background_capture_status():
    thread = app.config.get('BACKGROUND_CAPTURE_THREAD')
    if thread and thread.is_alive() and thread.is_running:
        next_in = compute_next_in_minutes(thread)
        return jsonify({'active': True, 'next_in': next_in})
    else:
        return jsonify({'active': False, 'next_in': None})


# -------------------------------
# Main
# -------------------------------
if __name__ == '__main__':
    # Start Cloudflare Quick Tunnel
    start_cloudflare_quick_tunnel()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000)