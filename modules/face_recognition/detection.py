import cv2
import os

HAAR_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'

class FaceDetector:
    def __init__(self):
        if not os.path.exists(HAAR_PATH):
            raise FileNotFoundError("No se encontró el clasificador Haarcascade.")
        self.detector = cv2.CascadeClassifier(HAAR_PATH)

    def detect(self, gray_frame, scaleFactor=1.3, minNeighbors=5):
        faces = self.detector.detectMultiScale(gray_frame, scaleFactor, minNeighbors)
        return faces
