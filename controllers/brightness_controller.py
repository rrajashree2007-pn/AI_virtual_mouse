"""
brightness_controller.py
Controls display brightness via the screen-brightness-control library,
which talks to WMI on Windows.
"""

try:
    import screen_brightness_control as sbc
    _SBC_AVAILABLE = True
except ImportError:
    _SBC_AVAILABLE = False


class BrightnessController:
    def __init__(self):
        self.available = _SBC_AVAILABLE

    def set_brightness_percent(self, percent):
        if not self.available:
            return
        percent = max(0, min(100, int(percent)))
        try:
            sbc.set_brightness(percent)
        except Exception:
            pass

    def get_brightness_percent(self):
        if not self.available:
            return 0
        try:
            values = sbc.get_brightness()
            return values[0] if values else 0
        except Exception:
            return 0

    def increase(self, step=5):
        self.set_brightness_percent(self.get_brightness_percent() + step)

    def decrease(self, step=5):
        self.set_brightness_percent(self.get_brightness_percent() - step)
