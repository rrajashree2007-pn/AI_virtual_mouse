"""
presentation_controller.py
Gesture-driven slide control for PowerPoint/PDF viewers in presenter
mode: next/previous slide, start/stop show, and a simple on-screen laser
pointer overlay driven by fingertip position.
"""

from controllers.keyboard_controller import KeyboardController


class PresentationController:
    def __init__(self):
        self._kb = KeyboardController()
        self.active = False
        self.pointer_enabled = False
        self.pointer_position = None  # (x, y) in screen coords, for overlay drawing

    def start_show(self):
        self._kb.press_key("f5")
        self.active = True

    def end_show(self):
        self._kb.press_key("esc")
        self.active = False

    def next_slide(self):
        self._kb.press_key("right")

    def previous_slide(self):
        self._kb.press_key("left")

    def toggle_black_screen(self):
        self._kb.press_key("b")

    def toggle_pointer(self):
        self.pointer_enabled = not self.pointer_enabled
        if not self.pointer_enabled:
            self.pointer_position = None
        return self.pointer_enabled

    def update_pointer(self, x, y):
        if self.pointer_enabled:
            self.pointer_position = (x, y)
