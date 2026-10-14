"""
test_core_logic.py
Unit tests for the parts of the system that don't require a camera,
microphone, or Windows-only APIs, so they can run in any CI environment.

Run with:  python -m unittest discover tests
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gestures.gesture_detector import GestureDetector
from gestures.gesture_actions import GestureActionMapper
from gestures.custom_gestures import CustomGestureStore, _normalize_landmarks
from utils.helpers import map_range, frame_to_screen, OneEuroFilter
from accessibility.accessibility_features import DwellClicker


class TestGestureDetector(unittest.TestCase):
    def test_open_palm_recognized_after_hold(self):
        detector = GestureDetector(hold_frames=3)
        fingers = [1, 1, 1, 1, 1]
        for _ in range(3):
            result = detector.classify(fingers)
        self.assertEqual(result, "open_palm")

    def test_pinch_overrides_finger_pattern(self):
        detector = GestureDetector(hold_frames=1, pinch_threshold=35)
        result = detector.classify([1, 1, 0, 0, 0], pinch_distance=10)
        self.assertEqual(result, "pinch")

    def test_unknown_pattern(self):
        detector = GestureDetector(hold_frames=1)
        result = detector.classify([1, 0, 1, 0, 1])
        self.assertEqual(result, "unknown")


class TestGestureActionMapper(unittest.TestCase):
    def test_dispatch_fires_callback(self):
        mapper = GestureActionMapper()
        calls = []
        mapper.bind("fist", lambda: calls.append("fired"))
        mapper.dispatch("open_palm")  # different gesture, no fire
        mapper.dispatch("fist")
        self.assertEqual(calls, ["fired"])

    def test_fire_once_does_not_repeat(self):
        mapper = GestureActionMapper()
        calls = []
        mapper.bind("fist", lambda: calls.append("fired"))
        mapper.dispatch("fist")
        mapper.dispatch("fist")  # same gesture again, should not re-fire
        self.assertEqual(len(calls), 1)


class TestCustomGestures(unittest.TestCase):
    def test_normalize_landmarks_translation_invariant(self):
        landmarks_a = [[0, 100, 100], [1, 120, 100], [2, 140, 100]]
        landmarks_b = [[0, 500, 500], [1, 520, 500], [2, 540, 500]]
        vec_a = _normalize_landmarks(landmarks_a)
        vec_b = _normalize_landmarks(landmarks_b)
        for a, b in zip(vec_a, vec_b):
            self.assertAlmostEqual(a, b, places=5)

    def test_add_and_match_sample(self):
        store = CustomGestureStore(path="/tmp/test_custom_gestures.json")
        sample = [[i, 100 + i * 5, 200 + i * 3] for i in range(21)]
        store.add_sample("my_gesture", sample)
        name, dist = store.match(sample)
        self.assertEqual(name, "my_gesture")
        self.assertLess(dist, 0.01)


class TestHelpers(unittest.TestCase):
    def test_map_range_basic(self):
        self.assertEqual(map_range(50, 0, 100, 0, 200), 100)
        self.assertEqual(map_range(-10, 0, 100, 0, 200), 0)   # clamped
        self.assertEqual(map_range(150, 0, 100, 0, 200), 200)  # clamped

    def test_frame_to_screen(self):
        x, y = frame_to_screen(480, 270, 960, 540, 1920, 1080, reduction=100)
        self.assertTrue(0 <= x <= 1920)
        self.assertTrue(0 <= y <= 1080)

    def test_one_euro_filter_smooths(self):
        f = OneEuroFilter()
        vals = [f.filter(v) for v in [0, 100, 0, 100, 0, 100]]
        # output should never wildly exceed the input range
        self.assertTrue(all(-10 <= v <= 110 for v in vals))


class TestDwellClicker(unittest.TestCase):
    def test_no_fire_before_dwell_time(self):
        clicker = DwellClicker(dwell_time=10.0, move_tolerance=5)
        fired = clicker.update(100, 100)
        self.assertFalse(fired)

    def test_resets_on_movement(self):
        clicker = DwellClicker(dwell_time=0.01, move_tolerance=5)
        clicker.update(100, 100)
        fired = clicker.update(200, 200)  # big jump resets the anchor
        self.assertFalse(fired)


if __name__ == "__main__":
    unittest.main()
