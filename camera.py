from datetime import datetime
import logging
import os
import cv2
import time

# This should only be used on Raspberry Pi with Picamera2 installed
try:
    from picamera2 import Picamera2
except ImportError:
    Picamera2 = None

# Function to capture image according the currently selected camera source
def capture_image(settings):
    if settings.get('camera_source') == 'droidcam':
        droidcam_capture_image(settings.get('droidcam_ip'), settings.get('droidcam_port'))
    else:
        picam_capture_image(settings.get('picam_awb_mode'))

# Function to capture image with droidcam
def droidcam_capture_image(ip, port):
    try:
        # URL of the DroidCam MJPEG stream (adjust if necessary)
        stream_url = f'http://{ip}:{port}/video'

        # Open the stream using OpenCV
        cap = cv2.VideoCapture(stream_url)

        # Check if the stream is available
        if not cap.isOpened():
            logging.error('DroidCam stream could not be opened.')
            return None

        # Read one frame from the stream
        ret, frame = cap.read()
        cap.release()

        if not ret or frame is None:
            logging.error('Failed to capture image from DroidCam.')
            return None

        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = os.path.join('static/images', f'image_{timestamp}.jpg')

        # Save the image to disk
        cv2.imwrite(filepath, frame)
        logging.info(f'Image captured and saved to {filepath}')
        return filepath

    except Exception as e:
        logging.error(f'Error capturing image: {e}')
        return None

# Function to capture image with picam on raspberry pi
def picam_capture_image(awb_mode):
    try:
        # Initialize the camera
        picam = Picamera2()
        picam.configure(picam.create_still_configuration())
        picam.set_controls({'AwbMode': awb_mode}) 
        picam.start()
        time.sleep(2)

        # Capture the image
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = f'static/images/image_{timestamp}.jpg'
        picam.capture_file(filepath)
        logging.info(f'Image captured and saved to {filepath}')
        
        # Stop and close the camera
        picam.stop()
        picam.close()

        return filepath
    
    except Exception as e:
        logging.error(f'Error capturing image: {e}')
        return None