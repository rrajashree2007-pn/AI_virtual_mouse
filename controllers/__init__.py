"""System-control modules: mouse, volume, brightness, keyboard, apps, windows, media."""
from .mouse_controller import MouseController
from .volume_controller import VolumeController
from .brightness_controller import BrightnessController
from .keyboard_controller import KeyboardController
from .application_controller import ApplicationController
from .window_controller import WindowController
from .media_controller import MediaController

__all__ = [
    "MouseController", "VolumeController", "BrightnessController",
    "KeyboardController", "ApplicationController", "WindowController",
    "MediaController",
]
