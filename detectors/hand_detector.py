"""
hand_detector.py
Wraps MediaPipe Hands to give a simple, reusable API for finding hand
landmarks, fingertip positions, "fingers up" state, and distances
between landmarks (used for pinch/click gestures).
"""

import math
import cv2
import mediapipe as mp


class HandDetector:
    """Detects one or more hands in a BGR frame and exposes landmark data."""

    # MediaPipe landmark indices for fingertips and their corresponding
    # "pip" joints (used to decide if a finger is extended).
    TIP_IDS = [4, 8, 12, 16, 20]

    def __init__(self, static_mode=False, max_hands=2,
                 detection_confidence=0.7, tracking_confidence=0.6):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=static_mode,
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.results = None
        self.landmark_list = []

    def find_hands(self, frame, draw=True):
        """Runs detection on a frame and optionally draws landmarks on it."""
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)

        if self.results.multi_hand_landmarks and draw:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )
        return frame

    def find_position(self, frame, hand_no=0):
        """Returns (landmark_list, bbox) for the requested hand index.

        landmark_list is a list of [id, x, y] in pixel coordinates.
        bbox is (xmin, ymin, xmax, ymax) or None if no hand is found.
        """
        self.landmark_list = []
        x_list, y_list = [], []
        bbox = None

        if self.results and self.results.multi_hand_landmarks:
            if hand_no >= len(self.results.multi_hand_landmarks):
                return self.landmark_list, bbox

            hand = self.results.multi_hand_landmarks[hand_no]
            h, w, _ = frame.shape
            for idx, lm in enumerate(hand.landmark):
                px, py = int(lm.x * w), int(lm.y * h)
                self.landmark_list.append([idx, px, py])
                x_list.append(px)
                y_list.append(py)

            if x_list and y_list:
                bbox = (min(x_list), min(y_list), max(x_list), max(y_list))

        return self.landmark_list, bbox

    def fingers_up(self):
        """Returns a list of 5 ints (thumb..pinky), 1 if extended else 0.

        Must be called after find_position(). Assumes a right hand held
        facing the camera for thumb logic; works reasonably for both
        hands for the other four fingers.
        """
        fingers = []
        if not self.landmark_list:
            return [0, 0, 0, 0, 0]

        # Thumb: compare x of tip vs the joint below it
        if self.landmark_list[self.TIP_IDS[0]][1] > self.landmark_list[self.TIP_IDS[0] - 1][1]:
            fingers.append(1 if self.landmark_list[self.TIP_IDS[0]][1] < self.landmark_list[self.TIP_IDS[0] - 2][1] else 0)
        else:
            fingers.append(1 if self.landmark_list[self.TIP_IDS[0]][1] > self.landmark_list[self.TIP_IDS[0] - 2][1] else 0)

        # Other four fingers: tip above pip joint (smaller y = higher on screen)
        for tip_id in self.TIP_IDS[1:]:
            if self.landmark_list[tip_id][2] < self.landmark_list[tip_id - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers

    def find_distance(self, p1, p2, frame=None, draw=True):
        """Euclidean distance between two landmark indices.

        Returns (distance, center_point, line_info) where line_info is
        (x1, y1, x2, y2) for optional drawing by the caller.
        """
        x1, y1 = self.landmark_list[p1][1], self.landmark_list[p1][2]
        x2, y2 = self.landmark_list[p2][1], self.landmark_list[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if frame is not None and draw:
            cv2.circle(frame, (x1, y1), 8, (255, 0, 255), cv2.FILLED)
            cv2.circle(frame, (x2, y2), 8, (255, 0, 255), cv2.FILLED)
            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 255), 2)
            cv2.circle(frame, (cx, cy), 8, (0, 255, 0), cv2.FILLED)

        distance = math.hypot(x2 - x1, y2 - y1)
        return distance, (cx, cy), (x1, y1, x2, y2)
