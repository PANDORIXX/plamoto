from datetime import datetime
import logging
import os
import cv2
import time
import shutil

# This should only be used on Raspberry Pi with Picamera2 installed
try:
    from picamera2 import Picamera2
except ImportError:
    Picamera2 = None

def droidcam_capture_image():
    try:
        # URL of the DroidCam MJPEG stream (adjust if necessary)
        stream_url = "http://192.168.178.69:4747/video"

        # Open the stream using OpenCV
        cap = cv2.VideoCapture(stream_url)

        # Check if the stream is available
        if not cap.isOpened():
            logging.error("DroidCam stream could not be opened.")
            return None

        # Read one frame from the stream
        ret, frame = cap.read()
        cap.release()

        if not ret or frame is None:
            logging.error("Failed to capture image from DroidCam.")
            return None

        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join("static/images", f"image_{timestamp}.jpg")

        # Save the image to disk
        # Rotate the image if needed
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        cv2.imwrite(filepath, frame)
        logging.info(f"Image saved to {filepath}")
        return filepath

    except Exception as e:
        logging.error(f"Error capturing image: {e}")
        return None
    
def picam_capture_image():
    try:
        # Initialize the camera
        picam = Picamera2()
        picam.configure(picam.create_still_configuration())
        picam.set_controls({"AwbMode": 0}) 
        picam.start()
        time.sleep(2)

        # Capture the image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"static/images/image_{timestamp}.jpg"
        picam.capture_file(filepath)
        logging.info(f"Image captured and saved to {filepath}")

        img = cv2.imread(filepath)
        img = cv2.rotate(img, cv2.ROTATE_180)
        cv2.imwrite(filepath, img)
        logging.info(f"Image saved after automatic white balance correction to {filepath}")
        
        # Stop and close the camera
        picam.stop()
        picam.close()

        return filepath
    
    except Exception as e:
        logging.error(f"Error capturing image: {e}")
        return None
    
def picam_test_capturing(): 
    def clear_test_images():
        test_image_dir = 'static/test_images'
        if os.path.exists(test_image_dir):
            shutil.rmtree(test_image_dir)
        os.makedirs(test_image_dir)

    # Test different exposure times and AWB modes
    exposure_times = [10000, 20000, 30000]
    awb_modes = [0, 1, 2, 3, 4, 5]

    # Clear test images
    clear_test_images()

    for exposure_time in exposure_times:
        for awb_mode in awb_modes:
            try:
                # Initialize the camera with test settings
                picam = Picamera2()
                picam.configure(picam.create_still_configuration())
                picam.set_controls({"ExposureTime": exposure_time, "AwbMode": awb_mode})
                picam.start()
                time.sleep(2)

                # Capture the test image
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = f"static/test_images/test_image_{timestamp}_exp{exposure_time}_awb{awb_mode}.jpg"
                picam.capture_file(filepath)
                logging.info(f"Test image captured with exposure {exposure_time} and AWB mode {awb_mode} saved to {filepath}")
            
                # Stop and close the camera
                picam.stop()
                picam.close()
            
            except Exception as e:
                logging.error(f"Error capturing test image with exposure {exposure_time} and AWB mode {awb_mode}: {e}")