import cv2
import numpy as np
import base64
from app.hand_detector import HandGestureDetector
import logging

logger = logging.getLogger(__name__)

class Camera:
# Modify the __init__ method to add more error information

    def __init__(self):
        try:
            logger.info("Initializing camera")
            self.camera = cv2.VideoCapture(0)
            
            if not self.camera.isOpened():
                logger.error("Could not open camera - camera not available or in use by another application")
                raise Exception("Could not open camera - camera not available or in use by another application")
            
            # Log camera properties
            width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
            logger.info(f"Camera opened with initial resolution: {width}x{height}")
            
            self.camera.set(3, 640)  # Width
            self.camera.set(4, 480)  # Height
            
            # Verify settings were applied
            actual_width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
            logger.info(f"Camera resolution set to: {actual_width}x{actual_height}")
            
            self.detector = HandGestureDetector()
            logger.info("Camera initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing camera: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    def get_frame(self):
        try:
            success, frame = self.camera.read()
            if not success:
                logger.warning("Failed to get frame from camera")
                return None, None
            
            # Flip horizontally for a selfie-view
            frame = cv2.flip(frame, 1)
            
            # Detect hand and get move
            move, processed_frame = self.detector.detect_fingers(frame)
            
            # Convert to JPEG
            ret, jpeg = cv2.imencode('.jpg', processed_frame)
            frame_bytes = jpeg.tobytes()
            encoded_frame = base64.b64encode(frame_bytes).decode('utf-8')
            
            return encoded_frame, move
        except Exception as e:
            logger.error(f"Error getting frame: {e}")
            return None, None
    
    def release(self):
        try:
            if hasattr(self, 'camera') and self.camera is not None:
                self.camera.release()
                logger.info("Camera released")
        except Exception as e:
            logger.error(f"Error releasing camera: {e}")