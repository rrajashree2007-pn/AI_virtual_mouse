"""
object_detector.py
Optional object detection used for things like detecting whether a phone
or paper document is being held up to camera during presentation mode.

If a Caffe/ONNX model is dropped into ai_models/ (see MODEL_PROTO /
MODEL_WEIGHTS below) it will be used for real detection via OpenCV's DNN
module. Otherwise it gracefully falls back to a simple motion/contour
based "something entered the frame" detector so the rest of the app
still works out of the box with zero extra downloads.
"""

import os
import cv2
import numpy as np

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai_models")
MODEL_PROTO = os.path.join(MODEL_DIR, "MobileNetSSD_deploy.prototxt")
MODEL_WEIGHTS = os.path.join(MODEL_DIR, "MobileNetSSD_deploy.caffemodel")

CLASSES = [
    "background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus",
    "car", "cat", "chair", "cow", "diningtable", "dog", "horse",
    "motorbike", "person", "pottedplant", "sheep", "sofa", "train",
    "tvmonitor", "cell phone", "book",
]


class ObjectDetector:
    def __init__(self, confidence_threshold=0.5):
        self.confidence_threshold = confidence_threshold
        self.net = None
        self._back_sub = None

        if os.path.exists(MODEL_PROTO) and os.path.exists(MODEL_WEIGHTS):
            self.net = cv2.dnn.readNetFromCaffe(MODEL_PROTO, MODEL_WEIGHTS)
        else:
            # Fallback: background-subtraction based motion/object presence
            self._back_sub = cv2.createBackgroundSubtractorMOG2(
                history=300, varThreshold=40, detectShadows=False
            )

    def detect(self, frame, draw=True):
        """Returns a list of dicts: {label, confidence, box:(x1,y1,x2,y2)}."""
        if self.net is not None:
            return self._detect_dnn(frame, draw)
        return self._detect_fallback(frame, draw)

    def _detect_dnn(self, frame, draw):
        h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
        self.net.setInput(blob)
        detections = self.net.forward()

        results = []
        for i in range(detections.shape[2]):
            confidence = float(detections[0, 0, i, 2])
            if confidence < self.confidence_threshold:
                continue
            class_id = int(detections[0, 0, i, 1])
            label = CLASSES[class_id] if class_id < len(CLASSES) else str(class_id)
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            x1, y1, x2, y2 = box.astype(int)
            results.append({"label": label, "confidence": confidence, "box": (x1, y1, x2, y2)})

            if draw:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{label} {confidence:.2f}", (x1, max(y1 - 10, 0)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        return results

    def _detect_fallback(self, frame, draw):
        """No pretrained model available: report large moving contours as
        generic 'object' detections. Good enough to trigger presence-based
        features without requiring any model download."""
        mask = self._back_sub.apply(frame)
        mask = cv2.medianBlur(mask, 5)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        results = []
        for c in contours:
            area = cv2.contourArea(c)
            if area < 4000:
                continue
            x, y, w, h = cv2.boundingRect(c)
            results.append({"label": "object", "confidence": None, "box": (x, y, x + w, y + h)})
            if draw:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 165, 255), 2)
                cv2.putText(frame, "object", (x, max(y - 10, 0)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 2)
        return results
