"""
media_controller.py
Sends OS-level media keys (play/pause, next, previous, mute) so gestures
can control whatever media player currently has focus/priority, without
needing per-app integration.
"""

try:
    import keyboard as kb
    _KB_AVAILABLE = True
except ImportError:
    _KB_AVAILABLE = False


class MediaController:
    def __init__(self):
        self.available = _KB_AVAILABLE

    def play_pause(self):
        if self.available:
            kb.send("play/pause media")

    def next_track(self):
        if self.available:
            kb.send("next track")

    def previous_track(self):
        if self.available:
            kb.send("previous track")

    def stop(self):
        if self.available:
            kb.send("stop media")

    def volume_mute(self):
        if self.available:
            kb.send("volume mute")

    def volume_up(self):
        if self.available:
            kb.send("volume up")

    def volume_down(self):
        if self.available:
            kb.send("volume down")
