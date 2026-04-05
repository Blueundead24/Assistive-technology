import threading
import time

import pyttsx3


class TTSManager:
    def __init__(self, cooldown_seconds: float):
        self.engine = pyttsx3.init()
        self.cooldown_seconds = cooldown_seconds
        self.last_spoken_time = 0.0
        self.last_spoken_key = ""
        self.engine_lock = threading.Lock()
        self.state_lock = threading.Lock()

    def speak_async(self, text: str):
        """Speak in a background thread so recognition loop stays responsive."""

        def _run():
            with self.engine_lock:
                self.engine.say(text)
                self.engine.runAndWait()

        threading.Thread(target=_run, daemon=True).start()

    def try_speak(self, text: str, key: str) -> bool:
        """Cooldown-protected speaker trigger."""
        now = time.time()
        should_speak = False

        with self.state_lock:
            if (now - self.last_spoken_time) >= self.cooldown_seconds or key != self.last_spoken_key:
                self.last_spoken_time = now
                self.last_spoken_key = key
                should_speak = True

        if should_speak:
            self.speak_async(text)
        return should_speak
