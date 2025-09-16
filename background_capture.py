import threading
import time
from camera import capture_image
from logger_setup import setup_logger
from config import Config

# -------------------------------
# Logging setup
# -------------------------------
logger = setup_logger(__name__)

_thread_instance = None

class BackgroundCaptureThread(threading.Thread):
    """Thread that schedules background captures at a fixed minute interval."""

    def __init__(self, interval_minutes: int, settings_getter):
        super().__init__(daemon=True)
        self.interval_min = max(Config.BACKGROUND_CAPTURE_MIN_INTERVAL, int(interval_minutes))  # safety: >= 1 minute
        self.interval_s = self.interval_min * 60
        self._stop_event = threading.Event()
        self.next_capture_time = None  # epoch seconds of next scheduled capture
        self.is_running = False
        self.settings_getter = settings_getter

    def run(self):
        self.is_running = True

        try:
            # Capture immediately
            capture_image(self.settings_getter())

            # Shedule next capture
            self.next_capture_time = time.time() + self.interval_s

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
                capture_image(self.settings_getter())

                # Schedule next
                self.next_capture_time = time.time() + self.interval_s
        finally:
            self.is_running = False

    def stop(self):
        """Signal the thread to stop and return immediately."""
        self._stop_event.set()

    def reset_schedule_now(self):
        """Reschedule next capture from 'now' (used after saving settings)."""
        self.next_capture_time = time.time() + self.interval_s


# -------------------------------
# Helpers
# -------------------------------

def start_background_thread(settings_getter, interval_minutes):
    """Start background capture thread using current settings."""
    global _thread_instance
    stop_background_thread(join=True)
    t = BackgroundCaptureThread(interval_minutes, settings_getter)
    t.start()
    _thread_instance = t
    logger.info(f"Background capture thread started (interval={interval_minutes} min).")
    return t

def stop_background_thread(join: bool = True):
    """Stop background capture thread if running."""
    global _thread_instance
    t = _thread_instance
    if t and t.is_alive():
        logger.info("Stopping background capture thread…")
        t.stop()
        if join:
            t.join(timeout=5.0)
        logger.info("Background capture thread stopped.")
    _thread_instance = None


def compute_next_in_minutes():
    """Return remaining minutes (int) until next capture, or None if unknown."""
    global _thread_instance
    t = _thread_instance
    if not t or not t.is_running or not t.next_capture_time:
        return None
    seconds_left = max(0, t.next_capture_time - time.time())
    return int(seconds_left // 60)