"""
keyboard_controller.py
Sends keystrokes to the OS via the 'keyboard' library. Backs both the
on-screen virtual keyboard (gui/) and gesture-triggered shortcuts
(e.g. copy/paste, undo, alt-tab).
"""

try:
    import keyboard as kb
    _KB_AVAILABLE = True
except ImportError:
    _KB_AVAILABLE = False


class KeyboardController:
    def __init__(self):
        self.available = _KB_AVAILABLE

    def type_text(self, text):
        if self.available:
            kb.write(text)

    def press_key(self, key_name):
        if self.available:
            kb.press_and_release(key_name)

    def press_combo(self, *keys):
        """e.g. press_combo('ctrl', 'c')"""
        if self.available:
            kb.press_and_release("+".join(keys))

    # Common shortcuts used elsewhere in the app
    def copy(self):
        self.press_combo("ctrl", "c")

    def paste(self):
        self.press_combo("ctrl", "v")

    def undo(self):
        self.press_combo("ctrl", "z")

    def redo(self):
        self.press_combo("ctrl", "y")

    def select_all(self):
        self.press_combo("ctrl", "a")

    def backspace(self):
        self.press_key("backspace")

    def enter(self):
        self.press_key("enter")

    def alt_tab(self):
        self.press_combo("alt", "tab")

    def screenshot(self):
        self.press_combo("windows", "shift", "s")
