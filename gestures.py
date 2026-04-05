from typing import Dict
import numpy as np
import json
import os


def normalize_landmarks(hand_landmarks) -> np.ndarray:
    coords = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark], dtype=np.float32)
    wrist = coords[0]
    centered = coords - wrist

    max_dist = np.max(np.linalg.norm(centered, axis=1))
    if max_dist < 1e-6:
        return centered

    return centered / max_dist


def gesture_distance(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean(np.linalg.norm(a - b, axis=1)))


class GestureStore:
    def __init__(self, file_path="gestures.json"):
        self._gestures: Dict[str, list] = {}
        self.file_path = file_path
        self.load()  # 🔥 auto load on startup

    def add_gesture(self, name: str, landmarks: np.ndarray) -> None:
        name = name.lower().strip()

        if name not in self._gestures:
            self._gestures[name] = []

        self._gestures[name].append(landmarks.copy())

        self.save()  # 🔥 auto save after training

    def count(self) -> int:
        return sum(len(v) for v in self._gestures.values())

    def match(self, live_landmarks: np.ndarray, threshold: float):
        if not self._gestures:
            return "none", None

        best_name = "none"
        best_dist = float("inf")

        for name, samples in self._gestures.items():
            for saved in samples:
                dist = gesture_distance(live_landmarks, saved)

                if dist < best_dist:
                    best_dist = dist
                    best_name = name

        if best_dist < threshold:
            return best_name, best_dist

        return "none", best_dist

    # 🔥 SAVE FILE
    def save(self):
        data = {
            name: [lm.tolist() for lm in samples]
            for name, samples in self._gestures.items()
        }

        with open(self.file_path, "w") as f:
            json.dump(data, f)

    # 🔥 LOAD FILE
    def load(self):
        if not os.path.exists(self.file_path):
            return

        with open(self.file_path, "r") as f:
            data = json.load(f)

        self._gestures = {
            name: [np.array(lm) for lm in samples]
            for name, samples in data.items()
        }