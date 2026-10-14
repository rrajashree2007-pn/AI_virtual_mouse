"""
face_detector.py
Wraps MediaPipe Face Mesh for face presence detection and landmark
extraction. Used by security (presence lock), eye tracking, and
accessibility features.
"""

import cv2
import mediapipe as mp


class FaceDetector:
    def __init__(self, max_faces=1, refine_landmarks=True,
                 detection_confidence=0.6, tracking_confidence=0.6):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=max_faces,
            refine_landmarks=refine_landmarks,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.draw_spec = self.mp_draw.DrawingSpec(thickness=1, circle_radius=1)
        self.results = None

    def find_face_mesh(self, frame, draw=True):
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.face_mesh.process(img_rgb)

        faces_landmarks = []
        h, w, _ = frame.shape

        if self.results.multi_face_landmarks:
            for face_landmarks in self.results.multi_face_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(
                        frame, face_landmarks,
                        self.mp_face_mesh.FACEMESH_CONTOURS,
                        self.draw_spec, self.draw_spec,
                    )
                points = [(int(lm.x * w), int(lm.y * h)) for lm in face_landmarks.landmark]
                faces_landmarks.append(points)

        return frame, faces_landmarks

    def is_face_present(self):
        """Cheap presence check without re-running detection."""
        return bool(self.results and self.results.multi_face_landmarks)
