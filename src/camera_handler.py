import cv2
import logging
import time

class CameraHandler:
    def __init__(self, source):
        self.source = source
        self.cap = None
        self.connect()

    def connect(self):
        """Establishes connection to the video source."""
        logging.info(f"Attempting to connect to camera source: {self.source}")
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            logging.error(f"Failed to open video source: {self.source}")
            self.cap = None
        else:
             logging.info(f"Successfully connected to video source: {self.source}")
             # Optionally set properties like resolution
             # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
             # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    def read_frame(self):
        """Reads a single frame from the video source."""
        if self.cap is None or not self.cap.isOpened():
            logging.warning(f"Camera source {self.source} not available. Attempting reconnect.")
            # Add a small delay before trying to reconnect
            time.sleep(2)
            self.connect()
            return None, None # Indicate failure to read frame

        ret, frame = self.cap.read()
        if not ret:
            logging.warning(f"Failed to read frame from source: {self.source}. End of stream or error?")
            # If it's a file, it might just be the end. If it's a stream, maybe try reconnecting.
            # For simplicity, we'll just return None here. A real system might handle differently.
            # self.release() # Optional: release if end of file
            return None, None
        return ret, frame

    def release(self):
        """Releases the video capture object."""
        if self.cap is not None:
            logging.info(f"Releasing video source: {self.source}")
            self.cap.release()
            self.cap = None

    def __del__(self):
        self.release() # Ensure release on object deletion