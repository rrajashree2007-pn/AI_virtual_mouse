"""
custom_gestures.py
Lets users record their own hand-shape gestures beyond the built-in set
(fist, palm, peace, etc). A gesture is stored as a normalized landmark
vector; matching uses a simple nearest-neighbour distance so no ML
dependency is required for basic use (see gesture_training.py for an
optional KNN/classifier-based approach).
"""

import json
import os
import math


def _normalize_landmarks(landmark_list):
    """Converts [[id,x,y], ...] into a translation/scale invariant vector
    relative to the wrist (landmark 0), so the same gesture matches
    regardless of hand position or distance from camera."""
    if not landmark_list:
        return []

    wrist_x, wrist_y = landmark_list[0][1], landmark_list[0][2]
    points = [(lm[1] - wrist_x, lm[2] - wrist_y) for lm in landmark_list]

    max_dist = max((math.hypot(x, y) for x, y in points), default=1) or 1
    normalized = []
    for x, y in points:
        normalized.append(x / max_dist)
        normalized.append(y / max_dist)
    return normalized


def _vector_distance(v1, v2):
    if len(v1) != len(v2) or not v1:
        return float("inf")
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)) / len(v1))


class CustomGestureStore:
    def __init__(self, path, match_threshold=0.15):
        self.path = path
        self.match_threshold = match_threshold
        self._gestures = {}
        self.load()

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r") as f:
                    self._gestures = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._gestures = {}
        else:
            self._gestures = {}

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(self._gestures, f, indent=2)

    def add_sample(self, name, landmark_list):
        """Adds a training sample for `name`, keeping a rolling average
        vector so recognition improves as more samples are added."""
        vector = _normalize_landmarks(landmark_list)
        if not vector:
            return False

        if name not in self._gestures:
            self._gestures[name] = {"vector": vector, "sample_count": 1}
        else:
            existing = self._gestures[name]
            n = existing["sample_count"]
            averaged = [
                (existing["vector"][i] * n + vector[i]) / (n + 1)
                for i in range(len(vector))
            ]
            existing["vector"] = averaged
            existing["sample_count"] = n + 1
        return True

    def delete(self, name):
        self._gestures.pop(name, None)

    def list_gestures(self):
        return list(self._gestures.keys())

    def match(self, landmark_list):
        """Returns (name, distance) of the closest custom gesture, or
        (None, None) if no gesture is within match_threshold."""
        vector = _normalize_landmarks(landmark_list)
        if not vector or not self._gestures:
            return None, None

        best_name, best_dist = None, float("inf")
        for name, data in self._gestures.items():
            dist = _vector_distance(vector, data["vector"])
            if dist < best_dist:
                best_name, best_dist = name, dist

        if best_dist <= self.match_threshold:
            return best_name, best_dist
        return None, None
