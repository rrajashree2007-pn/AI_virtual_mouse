"""
volume_controller.py
Controls the Windows master system volume via pycaw (which wraps the
Windows Core Audio APIs).
"""

try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    _PYCAW_AVAILABLE = True
except ImportError:
    _PYCAW_AVAILABLE = False


class VolumeController:
    def __init__(self):
        self.volume = None
        self.min_vol, self.max_vol = -65.25, 0.0

        if _PYCAW_AVAILABLE:
            try:
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                self.volume = cast(interface, POINTER(IAudioEndpointVolume))
                vol_range = self.volume.GetVolumeRange()
                self.min_vol, self.max_vol = vol_range[0], vol_range[1]
            except Exception:
                self.volume = None

    def _available(self):
        return self.volume is not None

    def set_volume_percent(self, percent):
        """percent in [0, 100]."""
        if not self._available():
            return
        percent = max(0, min(100, percent))
        # Map 0-100 -> min_vol..max_vol (which are in dB, e.g. -65.25..0)
        db = self.min_vol + (percent / 100.0) * (self.max_vol - self.min_vol)
        self.volume.SetMasterVolumeLevel(db, None)

    def get_volume_percent(self):
        if not self._available():
            return 0
        db = self.volume.GetMasterVolumeLevel()
        percent = (db - self.min_vol) / (self.max_vol - self.min_vol) * 100
        return max(0, min(100, round(percent)))

    def mute(self):
        if self._available():
            self.volume.SetMute(1, None)

    def unmute(self):
        if self._available():
            self.volume.SetMute(0, None)

    def toggle_mute(self):
        if not self._available():
            return
        is_muted = self.volume.GetMute()
        self.volume.SetMute(0 if is_muted else 1, None)

    def increase(self, step=5):
        self.set_volume_percent(self.get_volume_percent() + step)

    def decrease(self, step=5):
        self.set_volume_percent(self.get_volume_percent() - step)
