"""
eye_detector.py
Uses the landmarks produced by FaceDetector (MediaPipe Face Mesh) to
compute the Eye Aspect Ratio (EAR) for blink detection, and a rough
gaze-direction estimate. Useful for accessibility (blink-to-click,
gaze-assisted cursor) features.
"""

import math

# MediaPipe Face Mesh landmark indices around each eye
LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]

LEFT_IRIS = [474, 475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]


class EyeDetector:
    def __init__(self, blink_threshold=0.21, consecutive_frames=2):
        self.blink_threshold = blink_threshold
        self.consecutive_frames = consecutive_frames
        self._closed_counter = 0
        self.blink_count = 0

    @staticmethod
    def _euclidean(p1, p2):
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def _eye_aspect_ratio(self, points, eye_idx):
        try:
            p1, p2, p3, p4, p5, p6 = [points[i] for i in eye_idx]
        except IndexError:
            return None
        vertical_1 = self._euclidean(p2, p6)
        vertical_2 = self._euclidean(p3, p5)
        horizontal = self._euclidean(p1, p4)
        if horizontal == 0:
            return None
        return (vertical_1 + vertical_2) / (2.0 * horizontal)

    def get_ear(self, face_points):
        """Average eye-aspect-ratio across both eyes. None if unavailable."""
        left = self._eye_aspect_ratio(face_points, LEFT_EYE)
        right = self._eye_aspect_ratio(face_points, RIGHT_EYE)
        values = [v for v in (left, right) if v is not None]
        if not values:
            return None
        return sum(values) / len(values)

    def detect_blink(self, face_points):
        """Returns True exactly once when a blink completes."""
        ear = self.get_ear(face_points)
        if ear is None:
            return False

        if ear < self.blink_threshold:
            self._closed_counter += 1
            return False

        if self._closed_counter >= self.consecutive_frames:
            self.blink_count += 1
            self._closed_counter = 0
            return True

        self._closed_counter = 0
        return False

    def get_gaze_ratio(self, face_points):
        """Rough horizontal gaze ratio using iris landmarks (0=left, 1=right).

        Requires refine_landmarks=True in FaceDetector so iris points exist.
        Returns None if iris landmarks aren't available.
        """
        if len(face_points) <= max(LEFT_IRIS + RIGHT_IRIS):
            return None

        left_iris_x = sum(face_points[i][0] for i in LEFT_IRIS) / len(LEFT_IRIS)
        right_iris_x = sum(face_points[i][0] for i in RIGHT_IRIS) / len(RIGHT_IRIS)

        left_corner = face_points[LEFT_EYE[0]][0]
        left_corner_inner = face_points[LEFT_EYE[3]][0]
        right_corner = face_points[RIGHT_EYE[0]][0]
        right_corner_inner = face_points[RIGHT_EYE[3]][0]

        eye_width = abs(left_corner - left_corner_inner) + abs(right_corner_inner - right_corner)
        if eye_width == 0:
            return None

        avg_iris_x = (left_iris_x + right_iris_x) / 2
        avg_corner_x = (left_corner + right_corner_inner) / 2
        ratio = (avg_iris_x - avg_corner_x) / eye_width
        return max(0.0, min(1.0, ratio + 0.5))
