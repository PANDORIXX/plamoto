from datetime import datetime
import os
import cv2
import time
from logger_setup import setup_logger

# -------------------------------
# Logging setup
# -------------------------------
logger = setup_logger(__name__)

# Attempt to import Picamera2 (only available on Raspberry Pi)
try:
    from picamera2 import Picamera2
except ImportError:
    # If import fails, set Picamera2 to None (camera not available)
    Picamera2 = None

def capture_image(settings):
    """
    Capture an image based on the current camera source setting.
    Calls either the DroidCam or Picamera capture function.
    """
    if settings.get('camera_source') == 'droidcam':
        droidcam_capture_image(settings.get('droidcam_ip'), settings.get('droidcam_port'))
    else:
        picam_capture_image(settings.get('picam_awb_mode'))


def droidcam_capture_image(ip, port):
    """
    Capture an image from the DroidCam MJPEG stream using OpenCV.

    Args:
        ip (str): IP address of the DroidCam stream
        port (str/int): Port of the DroidCam stream

    Returns:
        str or None: Path to saved image file or None on failure
    """
    try:
        # Construct the MJPEG stream URL for DroidCam
        stream_url = f'http://{ip}:{port}/video'

        # Open the video stream using OpenCV's VideoCapture
        cap = cv2.VideoCapture(stream_url)

        # Check if the stream was successfully opened
        if not cap.isOpened():
            logger.error('DroidCam stream could not be opened.')
            return None

        # Read one frame from the video stream
        ret, frame = cap.read()

        # Release the VideoCapture resource immediately after reading
        cap.release()

        # Check if the frame was successfully captured
        if not ret or frame is None:
            logger.error('Failed to capture image from DroidCam.')
            return None

        # Generate a filename with current timestamp: YYYYMMDD_HHMMSS
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = os.path.join('static/images', f'image_{timestamp}.jpg')

        # Save the captured frame as a JPEG image
        cv2.imwrite(filepath, frame)
        logger.info(f'Image captured and saved to {filepath}')

        return filepath

    except Exception as e:
        # Log any unexpected error during capture
        logger.error(f'Error capturing image: {e}')
        return None


def picam_capture_image(awb_mode):
    """
    Capture an image using the Raspberry Pi Picamera2 with specified AWB mode.

    Args:
        awb_mode (str): Auto White Balance mode for the camera

    Returns:
        str or None: Path to saved image file or None on failure
    """
    try:
        # Initialize Picamera2 object
        picam = Picamera2()

        # Configure the camera for still image capture with default settings
        picam.configure(picam.create_still_configuration())

        # Set Auto White Balance mode control
        picam.set_controls({'AwbMode': awb_mode})

        # Start the camera and wait for it to stabilize
        picam.start()
        time.sleep(2)

        # Generate filename with current timestamp: YYYYMMDD_HHMMSS
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = f'static/images/image_{timestamp}.jpg'

        # Capture still image to file
        for attempt in range(3):
            try:
                picam.capture_file(filepath)
                break
            except Exception as e:
                logger.error(f"Error capturing image (attempt {attempt+1}): {e}")
                time.sleep(1)
        logger.info(f'Image captured and saved to {filepath}')

        # Stop and release camera resources
        picam.stop()
        picam.close()

        return filepath

    except Exception as e:
        # Log any error during capture
        logger.error(f'Error capturing image: {e}')
        return None

def picam_unavailability_logging(): 
    """Log that PiCamera2 is not available."""
    logger.error("PiCam not available.")