"""
gesture_training.py
Captures repeated hand-landmark samples for a new gesture name and feeds
them into CustomGestureStore. Also offers an optional scikit-learn KNN
classifier path (ai_models/gesture_classifier.py) for higher accuracy
once enough samples exist across multiple gesture classes.
"""

import time

from .custom_gestures import CustomGestureStore


class GestureTrainer:
    def __init__(self, custom_store: CustomGestureStore, samples_required=30, capture_interval=0.1):
        self.store = custom_store
        self.samples_required = samples_required
        self.capture_interval = capture_interval
        self.active = False
        self.gesture_name = None
        self.samples_collected = 0
        self._last_capture_time = 0.0

    def start(self, gesture_name):
        self.active = True
        self.gesture_name = gesture_name
        self.samples_collected = 0
        self._last_capture_time = 0.0

    def stop(self):
        self.active = False
        self.gesture_name = None

    def feed_frame(self, landmark_list):
        """Call this once per video frame while training is active. Returns
        True once the target sample count has been reached (training done)."""
        if not self.active or not landmark_list:
            return False

        now = time.time()
        if now - self._last_capture_time < self.capture_interval:
            return False

        added = self.store.add_sample(self.gesture_name, landmark_list)
        if added:
            self.samples_collected += 1
            self._last_capture_time = now

        if self.samples_collected >= self.samples_required:
            self.store.save()
            self.active = False
            return True
        return False

    def progress(self):
        if not self.active:
            return 0.0
        return min(1.0, self.samples_collected / self.samples_required)
