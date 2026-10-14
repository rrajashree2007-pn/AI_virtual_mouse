"""
window_controller.py
Manages OS windows: minimize, maximize, close, switch focus, list open
windows. Built on pygetwindow, with keyboard fallback (alt-tab, win+d)
for actions pygetwindow can't do reliably.
"""

try:
    import pygetwindow as gw
    _GW_AVAILABLE = True
except ImportError:
    _GW_AVAILABLE = False

from .keyboard_controller import KeyboardController


class WindowController:
    def __init__(self):
        self.available = _GW_AVAILABLE
        self._kb = KeyboardController()

    def list_windows(self):
        if not self.available:
            return []
        return [w.title for w in gw.getAllWindows() if w.title.strip()]

    def get_active_window(self):
        if not self.available:
            return None
        win = gw.getActiveWindow()
        return win.title if win else None

    def _find(self, title_substring):
        if not self.available:
            return None
        matches = [w for w in gw.getAllWindows() if title_substring.lower() in w.title.lower()]
        return matches[0] if matches else None

    def focus(self, title_substring):
        win = self._find(title_substring)
        if win:
            try:
                win.activate()
                return True
            except Exception:
                return False
        return False

    def minimize(self, title_substring=None):
        if title_substring:
            win = self._find(title_substring)
            if win:
                win.minimize()
                return True
            return False
        # Minimize the active window
        self._kb.press_combo("windows", "down")
        return True

    def maximize(self, title_substring=None):
        if title_substring:
            win = self._find(title_substring)
            if win:
                win.maximize()
                return True
            return False
        self._kb.press_combo("windows", "up")
        return True

    def close(self, title_substring=None):
        if title_substring:
            win = self._find(title_substring)
            if win:
                win.close()
                return True
            return False
        self._kb.press_combo("alt", "f4")
        return True

    def show_desktop(self):
        self._kb.press_combo("windows", "d")

    def switch_window(self):
        """Triggers the OS alt-tab switcher."""
        self._kb.alt_tab()

    def snap_left(self, title_substring=None):
        if title_substring:
            self.focus(title_substring)
        self._kb.press_combo("windows", "left")

    def snap_right(self, title_substring=None):
        if title_substring:
            self.focus(title_substring)
        self._kb.press_combo("windows", "right")
