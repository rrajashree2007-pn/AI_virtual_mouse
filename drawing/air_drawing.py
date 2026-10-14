import time
import cv2
import numpy as np


COLOR_PALETTE = [
    ("red", (0, 0, 255)),
    ("green", (0, 255, 0)),
    ("blue", (255, 0, 0)),
    ("yellow", (0, 255, 255)),
    ("white", (255, 255, 255)),
]


class AirCanvas:

    def __init__(self, width, height, brush_size=6, eraser_size=40):
        self.width = width
        self.height = height

        self.canvas = np.zeros(
            (height, width, 3),
            dtype=np.uint8
        )

        self.brush_size = brush_size
        self.eraser_size = eraser_size

        self.current_color = COLOR_PALETTE[0][1]
        self.color_name = COLOR_PALETTE[0][0]

        self.prev_point = None
        self.eraser_mode = False

    def set_color(self, name):
        for cname, color in COLOR_PALETTE:

            if cname == name:
                self.current_color = color
                self.color_name = name
                self.eraser_mode = False

                return True

        return False

    def cycle_color(self):
        names = [c[0] for c in COLOR_PALETTE]

        idx = names.index(self.color_name)

        next_color = names[
            (idx + 1) % len(names)
        ]

        self.set_color(next_color)

    def toggle_eraser(self):
        self.eraser_mode = not self.eraser_mode

    def draw_point(self, x, y):

        # Keep coordinates inside canvas
        x = max(0, min(int(x), self.width - 1))
        y = max(0, min(int(y), self.height - 1))

        if self.prev_point is None:
            self.prev_point = (x, y)
            return

        if self.eraser_mode:

            cv2.line(
                self.canvas,
                self.prev_point,
                (x, y),
                (0, 0, 0),
                self.eraser_size
            )

        else:

            cv2.line(
                self.canvas,
                self.prev_point,
                (x, y),
                self.current_color,
                self.brush_size
            )

        self.prev_point = (x, y)

    def lift_pen(self):
        self.prev_point = None

    def clear(self):

        self.canvas = np.zeros(
            (self.height, self.width, 3),
            dtype=np.uint8
        )

        self.prev_point = None

    def composite_onto(self, frame):

        # Get camera frame dimensions
        frame_height, frame_width = frame.shape[:2]

        # Resize canvas if camera resolution differs
        if (
            self.canvas.shape[0] != frame_height
            or self.canvas.shape[1] != frame_width
        ):

            self.canvas = cv2.resize(
                self.canvas,
                (frame_width, frame_height),
                interpolation=cv2.INTER_NEAREST
            )

            self.width = frame_width
            self.height = frame_height

        # Convert drawing to grayscale
        gray = cv2.cvtColor(
            self.canvas,
            cv2.COLOR_BGR2GRAY
        )

        # Create mask
        _, mask = cv2.threshold(
            gray,
            10,
            255,
            cv2.THRESH_BINARY
        )

        # Inverse mask
        mask_inv = cv2.bitwise_not(mask)

        # Camera background
        background = cv2.bitwise_and(
            frame,
            frame,
            mask=mask_inv
        )

        # Drawing layer
        drawing = cv2.bitwise_and(
            self.canvas,
            self.canvas,
            mask=mask
        )

        # Combine
        result = cv2.add(
            background,
            drawing
        )

        return result

    def save(self, path=None):

        path = path or f"drawing_{int(time.time())}.png"

        cv2.imwrite(
            path,
            self.canvas
        )

        return path