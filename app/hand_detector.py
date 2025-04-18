import cv2
from cvzone.HandTrackingModule import HandDetector
import logging

logger = logging.getLogger(__name__)

class HandGestureDetector:
    def __init__(self):
        try:
            logger.info("Initializing hand detector")
            self.detector = HandDetector(maxHands=1)
            logger.info("Hand detector initialized")
        except Exception as e:
            logger.error(f"Error initializing hand detector: {e}")
            raise
    
    def detect_fingers(self, frame):
        try:
            hands, img = self.detector.findHands(frame)
            
            if not hands:
                return None, img
            
            hand = hands[0]
            fingers = self.detector.fingersUp(hand)
            
            # Convert finger configuration to move number (0-5)
            move = None
            if fingers == [0, 0, 0, 0, 0]:
                move = 0
            elif fingers == [0, 1, 0, 0, 0]:
                move = 1
            elif fingers == [0, 1, 1, 0, 0]:
                move = 2
            elif fingers == [0, 1, 1, 1, 0]:
                move = 3
            elif fingers == [0, 1, 1, 1, 1]:
                move = 4
            elif fingers == [1, 1, 1, 1, 1]:
                move = 5
            
            return move, img
        except Exception as e:
            logger.error(f"Error detecting fingers: {e}")
            return None, frame