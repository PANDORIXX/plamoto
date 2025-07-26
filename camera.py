from datetime import datetime
import logging
import os
import cv2

def capture_image():
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