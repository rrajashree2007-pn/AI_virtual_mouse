"""Computer-vision detector modules (hands, face, eyes, objects)."""
from .hand_detector import HandDetector
from .face_detector import FaceDetector
from .eye_detector import EyeDetector
from .object_detector import ObjectDetector

__all__ = ["HandDetector", "FaceDetector", "EyeDetector", "ObjectDetector"]
