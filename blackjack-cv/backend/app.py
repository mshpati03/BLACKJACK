"""
Flask backend for Blackjack CV.
"""

import os
import time
import threading

import eventlet
eventlet.monkey_patch()

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO

from vision.camera_service import camera_service
from vision.detector import detector_service
from game.blackjack import BlackjackGame

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000", async_mode="eventlet")

game = BlackjackGame()
game_lock = threading.Lock()


@app.before_request
def _noop():
    pass


def startup():
    camera_service.start()
    detector_service.load_model()
    socketio.start_background_task(stream_camera)
    print("[App] Camera started. Streaming background task launched.")


def stream_camera():
    while True:
        try:
            data = detector_service.get_latest_frame_data()
            socketio.emit("camera_stream", data)
        except Exception as e:
            print(f"[Stream] Error: {e}")
        eventlet.sleep(0.07)


def make_capture():
    socketio.emit("game_state_update", game.get_state())

    detector_service.clear_history()

    consecutive_clear = 0
    deadline = time.time() + 12
    while time.time() < deadline:
        if detector_service.current_card_in_view() is None:
            consecutive_clear += 1
            if consecutive_clear >= 8:
                break
        else:
            consecutive_clear = 0
        eventlet.sleep(0.1)

    eventlet.sleep(0.2)

    for attempt in range(3):
        detector_service.clear_history()
        result = detector_service.capture_stable_card(duration_seconds=30)

        if result is None:
            return None

        if result["card"] in game.used_cards:
            print(f"[App] '{result['card']}' already used, waiting for different card...")
            consecutive_clear = 0
            deadline = time.time() + 12
            while time.time() < deadline:
                if detector_service.current_card_in_view() is None:
                    consecutive_clear += 1
                    if consecutive_clear >= 8:
                        break
                else:
                    consecutive_clear = 0
                eventlet.sleep(0.1)
            continue

        parts = result["card"].split(" of ")
        rank = parts[0] if len(parts) == 2 else result["card"]
        suit = parts[1] if len(parts) == 2 else ""
        phase = game.game_phase

        socketio.emit("card_captured", {
            "card": result["card"],
            "rank": rank,
            "suit": suit,
            "hidden": False,
            "phase": phase,
            "active_hand": game.active_hand,
            "confidence": result["confidence"],
        })

        consecutive_clear = 0
        deadline = time.time() + 10
        while time.time() < deadline:
            if detector_service.current_card_in_view() is None:
                consecutive_clear += 1
                if consecutive_clear >= 6:
                    break
            else:
                consecutive_clear = 0
            eventlet.sleep(0.1)

        detector_service.clear_history()
        return result

    return None


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "camera_running": camera_service.is_running(),
        "model_loaded": detector_service.is_model_loaded(),
        "detector_pipeline": detector_service.get_pipeline_settings(),
    })


@app.route("/api/state", methods=["GET"])
def get_state():
    with game_lock:
        state = game.get_state()
    return jsonify(state)


@app.route("/api/bet", methods=["POST"])
def place_bet():
    data = request.get_json(force=True)
    amount = data.get("amount")
    if amount is None:
        return jsonify({"error": "Missing 'amount' field."}), 400
    try:
        amount = int(amount)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid amount."}), 400

    with game_lock:
        detector_service.clear_history()
        game.reset_round_state()
        try:
            game.place_bet(amount)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        try:
            game.new_round(make_capture)
        except Exception as e:
            game.balance += amount
            game.reset_round_state()
            detector_service.clear_history()
            return jsonify({"error": str(e)}), 422
        state = game.get_state()

    return jsonify(state)


@app.route("/api/action", methods=["POST"])
def player_action():
    data = request.get_json(force=True)
    action = data.get("action", "").lower()
    if action not in ("hit", "stand", "double_down", "split"):
        return jsonify({"error": f"Unknown action: '{action}'."}), 400

    with game_lock:
        try:
            if action == "hit":
                game.hit(make_capture)
            elif action == "stand":
                game.stand(make_capture)
            elif action == "double_down":
                game.double_down(make_capture)
            elif action == "split":
                game.split(make_capture)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except RuntimeError as e:
            game.game_phase = "player_turn"
            return jsonify({"error": str(e)}), 422
        state = game.get_state()

    return jsonify(state)


@app.route("/api/detect", methods=["POST"])
def detect():
    result = detector_service.capture_stable_card(duration_seconds=30)
    if result is None:
        return jsonify({"detected_card": None, "confidence": 0.0})
    return jsonify({"detected_card": result["card"], "confidence": result["confidence"]})


@app.route("/api/new_round", methods=["POST"])
def new_round():
    with game_lock:
        game.reset_round_state()
        detector_service.clear_history()
        state = game.get_state()
    return jsonify(state)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5001"))
    startup()
    print(f"[App] Listening on http://0.0.0.0:{port}")
    socketio.run(app, host="0.0.0.0", port=port, debug=False)
