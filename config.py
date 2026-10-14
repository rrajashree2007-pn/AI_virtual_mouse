"""
config.py
Central configuration for AI Virtual Mouse.
Tweak these values to tune sensitivity, camera behaviour, and feature toggles.
"""

import os

# ----------------------------------------------------------------------
# Camera / Frame settings
# ----------------------------------------------------------------------
CAMERA_INDEX = 0
FRAME_WIDTH = 960
FRAME_HEIGHT = 540
FLIP_CAMERA = True          # mirror the webcam feed (feels natural to users)

# Region of the camera frame that maps to the full screen.
# Keeping a margin around the edges makes it easier to reach screen corners.
FRAME_REDUCTION = 100

# ----------------------------------------------------------------------
# Mouse settings
# ----------------------------------------------------------------------
MOUSE_SMOOTHENING = 5          # higher = smoother but laggier cursor
CLICK_DISTANCE_THRESHOLD = 35  # px distance between fingertips to register a "pinch" click
DOUBLE_CLICK_TIME = 0.35       # seconds between clicks to count as a double click
SCROLL_SENSITIVITY = 2

# ----------------------------------------------------------------------
# Gesture settings
# ----------------------------------------------------------------------
GESTURE_HOLD_FRAMES = 4        # frames a gesture must persist before it fires
CUSTOM_GESTURE_MATCH_THRESHOLD = 0.15  # lower = stricter matching

# ----------------------------------------------------------------------
# Volume / Brightness
# ----------------------------------------------------------------------
VOLUME_MIN_DISTANCE = 20
VOLUME_MAX_DISTANCE = 200
BRIGHTNESS_MIN_DISTANCE = 20
BRIGHTNESS_MAX_DISTANCE = 200

# ----------------------------------------------------------------------
# Feature toggles
# ----------------------------------------------------------------------
ENABLE_VOICE_CONTROL = True
ENABLE_ACCESSIBILITY_MODE = False
ENABLE_ANALYTICS = True
ENABLE_GUI = True

# ----------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DATABASE_PATH = os.path.join(BASE_DIR, "database", "virtual_mouse.db")
CUSTOM_GESTURES_PATH = os.path.join(BASE_DIR, "gestures", "custom_gestures.json")
GESTURE_MODEL_PATH = os.path.join(BASE_DIR, "ai_models", "gesture_model.joblib")

# ----------------------------------------------------------------------
# Colors (BGR, for OpenCV overlay drawing)
# ----------------------------------------------------------------------
COLOR_PRIMARY = (255, 0, 200)
COLOR_SUCCESS = (0, 255, 0)
COLOR_WARNING = (0, 165, 255)
COLOR_ERROR = (0, 0, 255)
COLOR_TEXT = (255, 255, 255)

# Ensure required directories exist
os.makedirs(os.path.join(BASE_DIR, "database"), exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)
