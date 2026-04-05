import threading
import time
from typing import Optional, Tuple

import cv2
import mediapipe as mp
import numpy as np

from config import (
    RECOGNITION_THRESHOLD,
)
from gestures import GestureStore, normalize_landmarks


# 🔥 CHANGE THIS IF YOUR PHONE IP CHANGES
PHONE_CAMERA_URL = "http://192.168.0.165:8080/video"


class CameraProcessor:
    def __init__(self, gesture_store: GestureStore):
        self.gesture_store = gesture_store

        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils

        # 🔥 Balanced MediaPipe (fast + stable)
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        # 🔥 Open phone stream with buffer control
        self.cap = cv2.VideoCapture(PHONE_CAMERA_URL)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if not self.cap.isOpened():
            raise RuntimeError("❌ Unable to open phone camera stream")

        self.lock = threading.Lock()
        self.latest_annotated_frame: Optional[np.ndarray] = None
        self.latest_landmarks: Optional[np.ndarray] = None

        self.detected_gesture = "none"
        self.match_distance: Optional[float] = None

    def process_camera_loop(self):
        frame_count = 0

        while True:
            ok, frame = self.cap.read()

            if not ok:
                time.sleep(0.02)
                continue

            frame_count += 1

            # 🔥 Skip frames (reduce lag)
            if frame_count % 2 != 0:
                continue

            # 🔥 Resize (BIG performance gain)
            frame = cv2.resize(frame, (320, 240))

            # 🔥 ORIENTATION FIX (choose ONE and stick to it)
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

            # 🔥 Mirror for selfie
            frame = cv2.flip(frame, 1)

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            results = self.hands.process(rgb)
            annotated = frame.copy()

            detected_name = "none"
            detected_landmarks = None
            detected_dist = None

            if results and results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                detected_landmarks = normalize_landmarks(hand_landmarks)

                self.mp_drawing.draw_landmarks(
                    annotated,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                )

                match_name, match_dist = self.gesture_store.match(
                    detected_landmarks, RECOGNITION_THRESHOLD
                )

                detected_name = match_name
                detected_dist = match_dist

            with self.lock:
                self.latest_annotated_frame = annotated
                self.latest_landmarks = detected_landmarks
                self.detected_gesture = detected_name
                self.match_distance = detected_dist

            # 🔥 Control CPU + smoothness
            time.sleep(0.03)

    def get_latest_landmarks(self) -> Optional[np.ndarray]:
        with self.lock:
            return None if self.latest_landmarks is None else self.latest_landmarks.copy()

    def get_recognition(self) -> Tuple[str, Optional[float]]:
        with self.lock:
            return self.detected_gesture, self.match_distance

    def generate_mjpeg_stream(self):
        while True:
            with self.lock:
                frame = None if self.latest_annotated_frame is None else self.latest_annotated_frame.copy()

            if frame is None:
                time.sleep(0.02)
                continue

            ok, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
            if not ok:
                continue

            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n'
            )

            # 🔥 Stream throttle
            time.sleep(0.03)