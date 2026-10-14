"""
accessibility_features.py
Adds accessibility-focused interaction modes on top of the core hand
gesture pipeline, useful for users with limited hand mobility:

- Dwell click: hovering the cursor still for N seconds triggers a click,
  removing the need for a pinch gesture.
- Blink click: uses EyeDetector's blink detection as a click trigger.
- Adjustable sensitivity: scales cursor movement for users with tremor
  or restricted range of motion.
"""

import time
import math


class DwellClicker:
    def __init__(self, dwell_time=1.2, move_tolerance=15):
        self.dwell_time = dwell_time
        self.move_tolerance = move_tolerance
        self._anchor = None
        self._anchor_time = None
        self._fired = False

    def update(self, x, y):
        """Call every frame with the current cursor position. Returns True
        exactly once when a dwell-click should fire."""
        if self._anchor is None:
            self._anchor = (x, y)
            self._anchor_time = time.time()
            self._fired = False
            return False

        dist = math.hypot(x - self._anchor[0], y - self._anchor[1])
        if dist > self.move_tolerance:
            self._anchor = (x, y)
            self._anchor_time = time.time()
            self._fired = False
            return False

        if not self._fired and (time.time() - self._anchor_time) >= self.dwell_time:
            self._fired = True
            return True
        return False

    def progress(self):
        if self._anchor_time is None:
            return 0.0
        return min(1.0, (time.time() - self._anchor_time) / self.dwell_time)


class SensitivityScaler:
    """Scales raw camera-space movement before it reaches the mouse
    controller, letting users with a smaller usable range of motion still
    reach the whole screen."""

    def __init__(self, sensitivity=1.5):
        self.sensitivity = sensitivity
        self._center = None

    def scale(self, x, y, frame_w, frame_h):
        if self._center is None:
            self._center = (frame_w / 2, frame_h / 2)
        cx, cy = self._center
        scaled_x = cx + (x - cx) * self.sensitivity
        scaled_y = cy + (y - cy) * self.sensitivity
        return max(0, min(frame_w, scaled_x)), max(0, min(frame_h, scaled_y))


class AccessibilityManager:
    """Bundles dwell-click, blink-click, and sensitivity scaling behind a
    single toggleable interface used by main.py."""

    def __init__(self, dwell_time=1.2, sensitivity=1.5):
        self.enabled = False
        self.dwell_clicker = DwellClicker(dwell_time=dwell_time)
        self.sensitivity_scaler = SensitivityScaler(sensitivity=sensitivity)
        self.blink_click_enabled = True

    def toggle(self):
        self.enabled = not self.enabled
        return self.enabled
