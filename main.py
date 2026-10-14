
"""
main.py
AI Virtual Mouse - entry point.

Modes:
    m - Mouse
    v - Volume
    b - Brightness
    p - Presentation
    d - Drawing

General:
    q - Quit
    a - Toggle accessibility mode
    l - Toggle auto-lock

Drawing:
    c - Clear canvas
    s - Save canvas
"""

import sys

import cv2

import config

from detectors.hand_detector import HandDetector
from detectors.face_detector import FaceDetector

from gestures.gesture_detector import GestureDetector
from gestures.gesture_actions import GestureActionMapper
from gestures.custom_gestures import CustomGestureStore

from controllers.mouse_controller import MouseController
from controllers.volume_controller import VolumeController
from controllers.brightness_controller import BrightnessController
from controllers.media_controller import MediaController
from controllers.window_controller import WindowController

from presentation.presentation_controller import PresentationController
from drawing.air_drawing import AirCanvas

from accessibility.accessibility_features import AccessibilityManager
from security.security_manager import SecurityManager

from analytics.analytics_manager import AnalyticsManager
from database.db_manager import DatabaseManager

from utils.helpers import frame_to_screen, FPSCounter


# ---------------------------------------------------------
# Optional GUI
# ---------------------------------------------------------

try:
    from gui.settings_gui import SettingsGUI

    _GUI_AVAILABLE = True

except ImportError:
    _GUI_AVAILABLE = False


# ---------------------------------------------------------
# Modes
# ---------------------------------------------------------

MODE_MOUSE = "mouse"
MODE_VOLUME = "volume"
MODE_BRIGHTNESS = "brightness"
MODE_PRESENTATION = "presentation"
MODE_DRAWING = "drawing"


# =========================================================
# Virtual Mouse Application
# =========================================================

class VirtualMouseApp:

    def __init__(self):

        # -------------------------------------------------
        # Camera
        # -------------------------------------------------

        self.cap = cv2.VideoCapture(config.CAMERA_INDEX)

        self.cap.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            config.FRAME_WIDTH
        )

        self.cap.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            config.FRAME_HEIGHT
        )

        # -------------------------------------------------
        # Detectors
        # -------------------------------------------------

        self.hand_detector = HandDetector(max_hands=1)

        self.face_detector = FaceDetector(max_faces=1)

        self.gesture_detector = GestureDetector(
            hold_frames=config.GESTURE_HOLD_FRAMES
        )

        self.custom_gestures = CustomGestureStore(
            config.CUSTOM_GESTURES_PATH,
            match_threshold=config.CUSTOM_GESTURE_MATCH_THRESHOLD
        )

        # -------------------------------------------------
        # Controllers
        # -------------------------------------------------

        self.mouse = MouseController(
            smoothening=config.MOUSE_SMOOTHENING
        )

        self.volume = VolumeController()

        self.brightness = BrightnessController()

        self.media = MediaController()

        self.windows = WindowController()

        self.presentation = PresentationController()

        self.canvas = AirCanvas(
            config.FRAME_WIDTH,
            config.FRAME_HEIGHT
        )

        self.accessibility = AccessibilityManager()

        self.security = SecurityManager()

        # -------------------------------------------------
        # Database / Analytics
        # -------------------------------------------------

        self.db = DatabaseManager(
            config.DATABASE_PATH
        )

        self.analytics = AnalyticsManager(
            db_manager=self.db
        )

        # -------------------------------------------------
        # Current mode
        # -------------------------------------------------

        self.mode = MODE_MOUSE

        self.fps_counter = FPSCounter()

        # =================================================
        # MOUSE DRAG STATE
        # =================================================

        self._drag_active = False

        # Position where pinch started
        self._pinch_start_x = None
        self._pinch_start_y = None

        # Minimum movement required before drag begins
        self._drag_threshold = 15

        # -------------------------------------------------
        # Gesture Action Mapper
        # -------------------------------------------------

        self.action_mapper = GestureActionMapper()

        # Load mouse bindings
        self._bind_mouse_mode()

        # -------------------------------------------------
        # GUI
        # -------------------------------------------------

        self.gui = None

        if _GUI_AVAILABLE and config.ENABLE_GUI:

            shared_settings = {

                "voice_control":
                    config.ENABLE_VOICE_CONTROL,

                "accessibility_mode":
                    config.ENABLE_ACCESSIBILITY_MODE,

                "analytics":
                    config.ENABLE_ANALYTICS,

                "auto_lock":
                    False,

                "mouse_smoothening":
                    config.MOUSE_SMOOTHENING,

                "click_distance_threshold":
                    config.CLICK_DISTANCE_THRESHOLD,
            }

            self.gui = SettingsGUI(
                shared_settings,
                on_change=self._on_gui_setting_change,
                analytics_manager=self.analytics
            )

            self.gui.start()

    # =====================================================
    # MODE SWITCHING
    # =====================================================

    def _switch_mode(self, new_mode):

        if new_mode == self.mode:
            return

        # Release mouse if switching modes during drag
        if self._drag_active:

            self.mouse.left_up()

            self._drag_active = False

        self._reset_pinch_state()

        self.mode = new_mode

        self.analytics.log_mode_switch(new_mode)

        self.action_mapper = GestureActionMapper()

        binder = {

            MODE_MOUSE:
                self._bind_mouse_mode,

            MODE_VOLUME:
                self._bind_volume_mode,

            MODE_BRIGHTNESS:
                self._bind_brightness_mode,

            MODE_PRESENTATION:
                self._bind_presentation_mode,

            MODE_DRAWING:
                self._bind_drawing_mode,

        }.get(new_mode)

        if binder:
            binder()

    # =====================================================
    # MOUSE MODE BINDINGS
    # =====================================================

    def _bind_mouse_mode(self):

        # ✊ Fist → Play / Pause
        self.action_mapper.bind(
            "fist",
            self.media.play_pause
        )

        # ✌️ Peace → Right click
        self.action_mapper.bind(
            "peace",
            self.mouse.right_click
        )

        # 🖐️ Open palm → Scroll
        self.action_mapper.bind(
            "open_palm",
            lambda: self.mouse.scroll(
                config.SCROLL_SENSITIVITY
            )
        )

    # =====================================================
    # VOLUME MODE
    # =====================================================

    def _bind_volume_mode(self):

        # ✊ Fist → Mute
        self.action_mapper.bind(
            "fist",
            self.volume.toggle_mute
        )

        # 👍 Thumbs up → Volume +5
        self.action_mapper.bind(
            "thumbs_up",
            lambda: self.volume.increase(5)
        )

        # 🤙 Pinky → Volume -5
        self.action_mapper.bind(
            "pinky",
            lambda: self.volume.decrease(5)
        )

    # =====================================================
    # BRIGHTNESS MODE
    # =====================================================

    def _bind_brightness_mode(self):

        # 👍 Thumbs up → Brightness +5
        self.action_mapper.bind(
            "thumbs_up",
            lambda: self.brightness.increase(5)
        )

        # 🤙 Pinky → Brightness -5
        self.action_mapper.bind(
            "pinky",
            lambda: self.brightness.decrease(5)
        )

    # =====================================================
    # PRESENTATION MODE
    # =====================================================

    def _bind_presentation_mode(self):

        # ☝️ Point → Next slide
        self.action_mapper.bind(
            "point",
            self.presentation.next_slide
        )

        # ✌️ Peace → Previous slide
        self.action_mapper.bind(
            "peace",
            self.presentation.previous_slide
        )

        # ✊ Fist → Toggle pointer
        self.action_mapper.bind(
            "fist",
            self.presentation.toggle_pointer
        )

        # 🖐️ Open palm → Black screen
        self.action_mapper.bind(
            "open_palm",
            self.presentation.toggle_black_screen
        )

    # =====================================================
    # DRAWING MODE
    # =====================================================

    def _bind_drawing_mode(self):

        # ✊ Fist → Toggle eraser
        self.action_mapper.bind(
            "fist",
            self.canvas.toggle_eraser
        )

        # ✌️ Peace → Change color
        self.action_mapper.bind(
            "peace",
            self.canvas.cycle_color
        )

        # 🖐️ Open palm → Lift pen
        self.action_mapper.bind(
            "open_palm",
            self.canvas.lift_pen
        )

    # =====================================================
    # GUI SETTINGS
    # =====================================================

    def _on_gui_setting_change(self, key, value):

        if key == "mouse_smoothening":

            self.mouse.smoothening = max(
                1,
                int(value)
            )

        elif key == "click_distance_threshold":

            config.CLICK_DISTANCE_THRESHOLD = int(value)

        elif key == "auto_lock":

            self.security.auto_lock_enabled = bool(value)

        elif key == "accessibility_mode":

            self.accessibility.enabled = bool(value)

    # =====================================================
    # PINCH RESET
    # =====================================================

    def _reset_pinch_state(self):

        self._pinch_start_x = None
        self._pinch_start_y = None

    # =====================================================
    # CAMERA LOOP
    # =====================================================

    def run(self):

        if not self.cap.isOpened():

            print(
                "ERROR: could not open webcam. "
                "Check CAMERA_INDEX in config.py."
            )

            sys.exit(1)

        print(
            "AI Virtual Mouse running."
        )

        print(
            "Press 'q' in the video window to quit."
        )

        try:

            while True:

                ok, frame = self.cap.read()

                if not ok:
                    continue

                # Mirror camera
                if config.FLIP_CAMERA:

                    frame = cv2.flip(
                        frame,
                        1
                    )

                # Process
                frame = self._process_frame(frame)

                # Draw information
                self._draw_overlay(frame)

                # Show
                cv2.imshow(
                    "AI Virtual Mouse",
                    frame
                )

                key = cv2.waitKey(1) & 0xFF

                if not self._handle_keypress(key):
                    break

        finally:

            self._shutdown()

    # =====================================================
    # PROCESS FRAME
    # =====================================================

    def _process_frame(self, frame):

        # -------------------------------------------------
        # Hand detection
        # -------------------------------------------------

        frame = self.hand_detector.find_hands(
            frame,
            draw=True
        )

        landmark_list, bbox = (
            self.hand_detector.find_position(frame)
        )

        # -------------------------------------------------
        # Face detection
        # -------------------------------------------------

        frame, face_points_list = (
            self.face_detector.find_face_mesh(
                frame,
                draw=False
            )
        )

        face_present = (
            self.face_detector.is_face_present()
        )

        self.security.report_face_presence(
            face_present
        )

        if self.security.should_lock():

            self.security.lock_workstation()

        # -------------------------------------------------
        # Hand found
        # -------------------------------------------------

        if landmark_list:

            # Get fingers
            fingers = (
                self.hand_detector.fingers_up()
            )

            # Thumb tip = 4
            # Index tip = 8
            pinch_dist, pinch_center, _ = (
                self.hand_detector.find_distance(
                    4,
                    8,
                    frame,
                    draw=False
                )
            )

            # Classify gesture
            gesture = (
                self.gesture_detector.classify(
                    fingers,
                    pinch_distance=pinch_dist
                )
            )

            self.analytics.log_gesture(
                gesture
            )

            # Handle gesture
            self._handle_gesture(
                gesture,
                landmark_list,
                pinch_center,
                pinch_dist,
                frame
            )

        else:

            # If hand disappears during drag,
            # release mouse button safely.
            if self._drag_active:

                self.mouse.left_up()

                self._drag_active = False

            self._reset_pinch_state()

        # -------------------------------------------------
        # Drawing canvas
        # -------------------------------------------------

        if self.mode == MODE_DRAWING:

            frame = (
                self.canvas.composite_onto(
                    frame
                )
            )

        return frame

    # =====================================================
    # HANDLE GESTURE
    # =====================================================

    def _handle_gesture(
        self,
        gesture,
        landmark_list,
        pinch_center,
        pinch_dist,
        frame
    ):

        # -------------------------------------------------
        # Index fingertip
        # -------------------------------------------------

        index_tip = landmark_list[8]

        # Camera → Screen
        screen_x, screen_y = frame_to_screen(

            index_tip[1],
            index_tip[2],

            config.FRAME_WIDTH,
            config.FRAME_HEIGHT,

            self.mouse.screen_w,
            self.mouse.screen_h,

            reduction=config.FRAME_REDUCTION,
        )

        # =================================================
        # MOUSE MODE
        # =================================================

        if self.mode == MODE_MOUSE:

            # ------------------------------------------------
            # ☝️ POINT
            # Move cursor
            # ------------------------------------------------

            if gesture == "point":

                # If currently dragging, release first
                if self._drag_active:

                    self.mouse.left_up()

                    self._drag_active = False

                self.mouse.move_smooth(
                    screen_x,
                    screen_y
                )

                self._reset_pinch_state()

            # ------------------------------------------------
            # 🤏 PINCH
            # Click / Drag
            # ------------------------------------------------

            elif gesture == "pinch":

                # First pinch frame
                if self._pinch_start_x is None:

                    self._pinch_start_x = screen_x
                    self._pinch_start_y = screen_y

                # Calculate movement
                dx = (
                    screen_x -
                    self._pinch_start_x
                )

                dy = (
                    screen_y -
                    self._pinch_start_y
                )

                distance = (
                    dx * dx +
                    dy * dy
                ) ** 0.5

                # ------------------------------------------------
                # Start drag after enough movement
                # ------------------------------------------------

                if distance > self._drag_threshold:

                    if not self._drag_active:

                        self.mouse.left_down()

                        self._drag_active = True

                    self.mouse.move_smooth(
                        screen_x,
                        screen_y
                    )

            # ------------------------------------------------
            # Any other gesture
            # ------------------------------------------------

            else:

                # Release active drag
                if self._drag_active:

                    self.mouse.left_up()

                    self._drag_active = False

                # ------------------------------------------------
                # Pinch ended without moving
                # = Normal left click
                # ------------------------------------------------

                if self._pinch_start_x is not None:

                    dx = (
                        screen_x -
                        self._pinch_start_x
                    )

                    dy = (
                        screen_y -
                        self._pinch_start_y
                    )

                    distance = (
                        dx * dx +
                        dy * dy
                    ) ** 0.5

                    if distance <= self._drag_threshold:

                        self.mouse.left_click()

                        self.analytics.log_click()

                self._reset_pinch_state()

        # =================================================
        # VOLUME MODE
        # =================================================

        elif self.mode == MODE_VOLUME:

            pass

        # =================================================
        # BRIGHTNESS MODE
        # =================================================

        elif self.mode == MODE_BRIGHTNESS:

            pass

        # =================================================
        # PRESENTATION MODE
        # =================================================

        elif self.mode == MODE_PRESENTATION:

            # Move presentation pointer
            self.presentation.update_pointer(
                int(screen_x),
                int(screen_y)
            )

        # =================================================
        # DRAWING MODE
        # =================================================

        elif self.mode == MODE_DRAWING:

            # ☝️ Point → Draw
            if gesture == "point":

                self.canvas.draw_point(
                    index_tip[1],
                    index_tip[2]
                )

            else:

                self.canvas.lift_pen()

        # =================================================
        # Fire one-time gesture actions
        # =================================================

        self.action_mapper.dispatch(
            gesture
        )

    # =====================================================
    # SCREEN OVERLAY
    # =====================================================

    def _draw_overlay(self, frame):

        fps = self.fps_counter.update()

        cv2.putText(
            frame,
            f"FPS: {int(fps)}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            config.COLOR_TEXT,
            2
        )

        cv2.putText(
            frame,
            f"Mode: {self.mode.upper()}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            config.COLOR_PRIMARY,
            2
        )

        cv2.putText(
            frame,
            f"Gesture: {self.gesture_detector.stable_gesture}",
            (10, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            config.COLOR_SUCCESS,
            2
        )

        # Show drag status
        if self._drag_active:

            cv2.putText(
                frame,
                "DRAGGING",
                (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                config.COLOR_SUCCESS,
                2
            )

    # =====================================================
    # KEYBOARD
    # =====================================================

    def _handle_keypress(self, key):

        # Q → Quit
        if key == ord("q"):

            return False

        # M → Mouse
        elif key == ord("m"):

            self._switch_mode(
                MODE_MOUSE
            )

        # V → Volume
        elif key == ord("v"):

            self._switch_mode(
                MODE_VOLUME
            )

        # B → Brightness
        elif key == ord("b"):

            self._switch_mode(
                MODE_BRIGHTNESS
            )

        # P → Presentation
        elif key == ord("p"):

            self._switch_mode(
                MODE_PRESENTATION
            )

        # D → Drawing
        elif key == ord("d"):

            self._switch_mode(
                MODE_DRAWING
            )

        # A → Accessibility
        elif key == ord("a"):

            self.accessibility.toggle()

        # L → Auto lock
        elif key == ord("l"):

            self.security.toggle_auto_lock()

        # C → Clear drawing
        elif (
            key == ord("c")
            and self.mode == MODE_DRAWING
        ):

            self.canvas.clear()

        # S → Save drawing
        elif (
            key == ord("s")
            and self.mode == MODE_DRAWING
        ):

            path = self.canvas.save()

            print(
                f"Drawing saved to {path}"
            )

        return True

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def _shutdown(self):

        # Safety: release mouse if dragging
        if self._drag_active:

            self.mouse.left_up()

            self._drag_active = False

        self.analytics.end_session()

        self.cap.release()

        cv2.destroyAllWindows()

        print(
            "Session summary:",
            self.analytics.summary()
        )


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    app = VirtualMouseApp()

    app.run()
