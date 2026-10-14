"""
security_manager.py
Lightweight security features built on face presence detection:

- Auto-lock: locks the Windows session if no face has been seen in
  front of the camera for a configurable timeout (protects against
  someone using your PC while you've stepped away).
- Gesture PIN unlock: define a short sequence of gestures as a "PIN"
  that must be entered in order to unlock/authorize a sensitive action
  inside the app itself (not a substitute for Windows login security).
"""

import ctypes
import time

user32 = ctypes.windll.user32 if hasattr(ctypes, "windll") else None


class SecurityManager:
    def __init__(self, absence_timeout=30.0):
        self.absence_timeout = absence_timeout
        self._last_seen = time.time()
        self.auto_lock_enabled = False

        self._pin_sequence = []
        self._pin_progress = []
        self._pin_gesture_timeout = 3.0
        self._last_pin_gesture_time = 0.0

    # ------------------------------------------------------------------
    def report_face_presence(self, present):
        if present:
            self._last_seen = time.time()

    def seconds_since_last_seen(self):
        return time.time() - self._last_seen

    def should_lock(self):
        return self.auto_lock_enabled and self.seconds_since_last_seen() >= self.absence_timeout

    def lock_workstation(self):
        if user32:
            user32.LockWorkStation()

    def toggle_auto_lock(self):
        self.auto_lock_enabled = not self.auto_lock_enabled
        self._last_seen = time.time()
        return self.auto_lock_enabled

    # ------------------------------------------------------------------
    def set_pin_sequence(self, gesture_names):
        """e.g. set_pin_sequence(['fist', 'open_palm', 'peace'])"""
        self._pin_sequence = list(gesture_names)
        self._pin_progress = []

    def feed_gesture(self, gesture_name):
        """Feed each newly-fired gesture in; returns True once the full
        PIN sequence has been entered correctly in order within the
        per-gesture timeout, resets on mistake or timeout."""
        if not self._pin_sequence or gesture_name in ("none", "unknown"):
            return False

        now = time.time()
        if self._pin_progress and (now - self._last_pin_gesture_time) > self._pin_gesture_timeout:
            self._pin_progress = []

        expected = self._pin_sequence[len(self._pin_progress)]
        if gesture_name == expected:
            self._pin_progress.append(gesture_name)
            self._last_pin_gesture_time = now
        else:
            self._pin_progress = []
            return False

        if len(self._pin_progress) == len(self._pin_sequence):
            self._pin_progress = []
            return True
        return False

    def pin_progress_fraction(self):
        if not self._pin_sequence:
            return 0.0
        return len(self._pin_progress) / len(self._pin_sequence)
