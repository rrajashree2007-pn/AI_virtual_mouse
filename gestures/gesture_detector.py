"""
gesture_detector.py
Turns raw "fingers up" patterns (from HandDetector.fingers_up) and
fingertip distances into a named, stable gesture, with simple debouncing
so a gesture must be held for a few frames before it "fires".
"""

from collections import deque

# fingers_up() order: [thumb, index, middle, ring, pinky]
BUILTIN_GESTURES = {
    (0, 0, 0, 0, 0): "fist",
    (1, 1, 1, 1, 1): "open_palm",
    (0, 1, 0, 0, 0): "point",
    (0, 1, 1, 0, 0): "peace",
    (1, 0, 0, 0, 0): "thumbs_up",
    (0, 0, 0, 0, 1): "pinky",
    (1, 1, 0, 0, 1): "spiderman",
    (1, 1, 1, 1, 0): "four",
    (0, 1, 1, 1, 0): "three",
}


class GestureDetector:
    def __init__(self, hold_frames=4, pinch_threshold=35):
        self.hold_frames = hold_frames
        self.pinch_threshold = pinch_threshold
        self._history = deque(maxlen=hold_frames)
        self.stable_gesture = "none"

    def classify(self, fingers, pinch_distance=None):
        """fingers: list of 5 ints. pinch_distance: distance between thumb
        and index tip, used to detect a 'pinch' regardless of other
        finger positions (useful as a click trigger)."""
        if pinch_distance is not None and pinch_distance < self.pinch_threshold:
            raw_gesture = "pinch"
        else:
            raw_gesture = BUILTIN_GESTURES.get(tuple(fingers), "unknown")

        self._history.append(raw_gesture)
        self._debounce()
        return self.stable_gesture

    def _debounce(self):
        """Only accept a new stable gesture once it has been seen for
        `hold_frames` consecutive frames, to avoid flicker."""
        if len(self._history) < self.hold_frames:
            return
        if all(g == self._history[0] for g in self._history):
            self.stable_gesture = self._history[0]

    def reset(self):
        self._history.clear()
        self.stable_gesture = "none"
