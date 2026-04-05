import threading
import time
from typing import Dict

from flask import Flask, Response, jsonify, render_template, request

from camera import CameraProcessor
from config import CONTEXTS, DEFAULT_CONTEXT, SPEECH_COOLDOWN_SECONDS
from gestures import GestureStore
from tts import TTSManager

# 🔥 Capture storage
captured_landmarks = None
capture_lock = threading.Lock()

app = Flask(__name__)

store = GestureStore()
camera = CameraProcessor(store)
tts = TTSManager(cooldown_seconds=SPEECH_COOLDOWN_SECONDS)

gesture_context_map = {
    "thumbs_up": {
        "cafe": "One coffee please",
        "hospital": "I am okay",
        "college": "Present",
        "bank": "Confirm"
    },
    "stop": {
        "cafe": "Stop order",
        "hospital": "Emergency stop",
        "college": "Wait",
        "bank": "Cancel"
    },
    "peace": {
        "cafe": "Two items",
        "hospital": "Need assistance",
        "college": "Break",
        "bank": "Check balance"
    }
}

state_lock = threading.Lock()
state: Dict[str, str] = {
    "context": DEFAULT_CONTEXT,
    "gesture": "none",
    "phrase": "Waiting for gesture...",
}


def phrase_for(gesture_name: str, context_name: str) -> str:
    gesture_name = gesture_name.lower()

    if gesture_name in gesture_context_map:
        msg = gesture_context_map[gesture_name].get(context_name)
        if msg:
            return msg

    return gesture_name


def recognition_state_loop():
    while True:
        gesture_name, _ = camera.get_recognition()

        with state_lock:
            context_name = state["context"]

            if gesture_name == "none":
                phrase = "Waiting for gesture..."
            else:
                phrase = phrase_for(gesture_name, context_name)

            state["gesture"] = gesture_name
            state["phrase"] = phrase

        if gesture_name != "none":
            speech_key = f"{context_name}:{gesture_name}"
            tts.try_speak(phrase, speech_key)


@app.route("/")
def index():
    return render_template("index.html", contexts=CONTEXTS)


@app.route("/video_feed")
def video_feed():
    return Response(
        camera.generate_mjpeg_stream(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# 🔥 FIXED TRAIN ROUTE (uses captured gesture)
@app.route("/train", methods=["POST"])
def train():
    global captured_landmarks

    data = request.get_json(silent=True) or {}

    gesture_name = str(data.get("gesture_name", "")).strip().lower()
    messages = data.get("messages", {})

    if not gesture_name:
        return jsonify({"error": "gesture_name is required"}), 400

    # ✅ Use captured gesture instead of live one
    with capture_lock:
        landmarks = None if captured_landmarks is None else captured_landmarks.copy()

    if landmarks is None:
        return jsonify({"error": "No captured gesture"}), 400

    # store gesture
    store.add_gesture(gesture_name, landmarks)

    # store messages
    gesture_context_map[gesture_name] = {
        "cafe": str(messages.get("cafe", "")).strip(),
        "hospital": str(messages.get("hospital", "")).strip(),
        "college": str(messages.get("college", "")).strip(),
        "bank": str(messages.get("bank", "")).strip()
    }

    return jsonify({
        "message": "Gesture trained",
        "gesture_name": gesture_name
    })


@app.route("/get_state")
def get_state():
    with state_lock:
        snapshot = dict(state)

    snapshot["trained_gesture_count"] = store.count()
    return jsonify(snapshot)


@app.route("/set_context", methods=["POST"])
def set_context():
    data = request.get_json(silent=True) or {}
    context_name = str(data.get("context", "")).strip().lower()

    if context_name not in CONTEXTS:
        return jsonify({"error": f"Invalid context. Choose one of: {CONTEXTS}"}), 400

    with state_lock:
        state["context"] = context_name

    return jsonify({"context": context_name})


# 🔥 FIXED CAPTURE ROUTE (WAIT + STABLE)
@app.route("/capture_landmarks")
def capture_landmarks():
    global captured_landmarks

    timeout = 2.0  # seconds
    start_time = time.time()

    while time.time() - start_time < timeout:
        landmarks = camera.get_latest_landmarks()

        if landmarks is not None:
            with capture_lock:
                captured_landmarks = landmarks.copy()
            return jsonify({"message": "Gesture captured"})

        time.sleep(0.05)

    return jsonify({"error": "No hand detected"}), 400


def start_background_threads():
    threading.Thread(target=camera.process_camera_loop, daemon=True).start()
    threading.Thread(target=recognition_state_loop, daemon=True).start()


if __name__ == "__main__":
    start_background_threads()
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)