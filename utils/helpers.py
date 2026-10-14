"""
helpers.py
Small, dependency-free utility functions shared across the project:
coordinate mapping between camera frame and screen, FPS measurement,
and a One-Euro-style smoothing filter for reducing hand-tracking jitter.
"""

import time
import math


def map_range(value, in_min, in_max, out_min, out_max):
    """Linearly maps value from [in_min, in_max] to [out_min, out_max],
    clamping the input first."""
    value = max(min(value, in_max), in_min)
    if in_max == in_min:
        return out_min
    return out_min + (out_max - out_min) * (value - in_min) / (in_max - in_min)


def frame_to_screen(x, y, frame_w, frame_h, screen_w, screen_h, reduction=100):
    """Maps a point in a reduced camera region to full-screen coordinates,
    so the user doesn't need to reach the extreme edges of the camera
    frame to reach the edges of the screen."""
    screen_x = map_range(x, reduction, frame_w - reduction, 0, screen_w)
    screen_y = map_range(y, reduction, frame_h - reduction, 0, screen_h)
    return screen_x, screen_y


class FPSCounter:
    def __init__(self, smoothing=0.9):
        self.smoothing = smoothing
        self._prev_time = time.time()
        self.fps = 0.0

    def update(self):
        now = time.time()
        dt = now - self._prev_time
        self._prev_time = now
        if dt > 0:
            instant_fps = 1.0 / dt
            self.fps = self.smoothing * self.fps + (1 - self.smoothing) * instant_fps
        return self.fps


class OneEuroFilter:
    """Reduces jitter in noisy tracking data while keeping latency low
    during fast movement. See Casiez et al., '1€ Filter' (2012)."""

    def __init__(self, freq=30, min_cutoff=1.0, beta=0.02, d_cutoff=1.0):
        self.freq = freq
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self.x_prev = None
        self.dx_prev = 0.0
        self.t_prev = None

    @staticmethod
    def _alpha(cutoff, freq):
        tau = 1.0 / (2 * math.pi * cutoff)
        te = 1.0 / freq
        return 1.0 / (1.0 + tau / te)

    def filter(self, x, timestamp=None):
        t = timestamp if timestamp is not None else time.time()

        if self.t_prev is None:
            self.t_prev = t
            self.x_prev = x
            return x

        dt = max(t - self.t_prev, 1e-6)
        self.freq = 1.0 / dt

        dx = (x - self.x_prev) * self.freq
        a_d = self._alpha(self.d_cutoff, self.freq)
        dx_hat = a_d * dx + (1 - a_d) * self.dx_prev

        cutoff = self.min_cutoff + self.beta * abs(dx_hat)
        a = self._alpha(cutoff, self.freq)
        x_hat = a * x + (1 - a) * self.x_prev

        self.x_prev, self.dx_prev, self.t_prev = x_hat, dx_hat, t
        return x_hat
