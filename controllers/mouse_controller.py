"""
mouse_controller.py
Moves and clicks the real Windows cursor via ctypes calls into user32.dll.
Using raw WinAPI (instead of only pyautogui) keeps cursor movement fast
and avoids pyautogui's built-in failsafe pause, which matters for a
smooth real-time gesture-driven cursor.
"""

import ctypes
import time

user32 = ctypes.windll.user32 if hasattr(ctypes, "windll") else None

# mouse_event flags
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_WHEEL = 0x0800


class MouseController:
    def __init__(self, smoothening=5, double_click_time=0.35):
        self.smoothening = max(1, smoothening)
        self.double_click_time = double_click_time
        self.prev_x, self.prev_y = 0, 0
        self.curr_x, self.curr_y = 0, 0
        self._last_click_time = 0.0
        self.screen_w, self.screen_h = self.get_screen_size()

    # ------------------------------------------------------------------
    @staticmethod
    def get_screen_size():
        if user32 is None:
            return 1920, 1080
        return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

    # ------------------------------------------------------------------
    def move_smooth(self, target_x, target_y):
        """Move the cursor toward (target_x, target_y) with smoothing to
        reduce jitter from noisy hand-tracking coordinates."""
        self.curr_x = self.prev_x + (target_x - self.prev_x) / self.smoothening
        self.curr_y = self.prev_y + (target_y - self.prev_y) / self.smoothening

        x = int(max(0, min(self.screen_w - 1, self.curr_x)))
        y = int(max(0, min(self.screen_h - 1, self.curr_y)))

        if user32:
            user32.SetCursorPos(x, y)

        self.prev_x, self.prev_y = self.curr_x, self.curr_y
        return x, y

    def move_to(self, x, y):
        """Instant move, no smoothing."""
        x = int(max(0, min(self.screen_w - 1, x)))
        y = int(max(0, min(self.screen_h - 1, y)))
        if user32:
            user32.SetCursorPos(x, y)

    def get_position(self):
        if user32 is None:
            return 0, 0
        pt = ctypes.wintypes.POINT() if hasattr(ctypes, "wintypes") else None
        if pt is None:
            import ctypes.wintypes as wintypes
            pt = wintypes.POINT()
        user32.GetCursorPos(ctypes.byref(pt))
        return pt.x, pt.y

    # ------------------------------------------------------------------
    def left_click(self):
        if not user32:
            return
        user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    def right_click(self):
        if not user32:
            return
        user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)

    def double_click(self):
        self.left_click()
        time.sleep(0.08)
        self.left_click()

    def maybe_double_click(self):
        """Call this on every single-click event; it decides internally
        whether two rapid clicks should be treated as a double click."""
        now = time.time()
        is_double = (now - self._last_click_time) < self.double_click_time
        self._last_click_time = now
        self.left_click()
        return is_double

    def left_down(self):
        if user32:
            user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)

    def left_up(self):
        if user32:
            user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    def scroll(self, amount):
        """Positive scrolls up, negative scrolls down. amount in wheel clicks."""
        if user32:
            user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, int(amount * 120), 0)

    def drag_to(self, x, y):
        """Perform a drag: press left button, move, release."""
        self.left_down()
        self.move_to(x, y)
        time.sleep(0.05)
        self.left_up()
