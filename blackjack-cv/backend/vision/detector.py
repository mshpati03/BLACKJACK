"""
YOLO card detection with separate preview vs inference framing.
"""

import base64
import logging
import os
import time
from collections import Counter, deque

import cv2
from ultralytics import YOLO

from game.card_labels import normalize_card_label
from vision.camera_service import camera_service

logger = logging.getLogger(__name__)
if not logger.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("[%(name)s] %(levelname)s: %(message)s"))
    logger.addHandler(_h)
logger.setLevel(logging.INFO)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "best.pt")


def _env_bool(name, default):
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def _env_int(name, default):
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw.strip())
    except ValueError:
        return default


def _env_float(name, default):
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return float(raw.strip())
    except ValueError:
        return default


UNMIRROR_FOR_INFERENCE = _env_bool("BLACKJACK_CV_UNMIRROR_FOR_INFERENCE", True)
MIRROR_PREVIEW = _env_bool("BLACKJACK_CV_MIRROR_PREVIEW", False)
INFERENCE_MIN_CONF = _env_float("BLACKJACK_CV_INFERENCE_MIN_CONF", 0.48)
STABLE_AVG_CONF = _env_float("BLACKJACK_CV_STABLE_AVG_CONF", 0.58)
YOLO_IOU = _env_float("BLACKJACK_CV_YOLO_IOU", 0.5)
YOLO_MAX_DET = _env_int("BLACKJACK_CV_YOLO_MAX_DET", 5)
WINDOW_FRAMES = _env_int("BLACKJACK_CV_WINDOW_FRAMES", 12)
MIN_AGREE = _env_int("BLACKJACK_CV_MIN_AGREE", 5)
HISTORY_LENGTH = _env_int("BLACKJACK_CV_HISTORY_LENGTH", 28)
CLEAR_STREAK = _env_int("BLACKJACK_CV_CLEAR_STREAK", 6)
LABEL_SWITCH_STREAK = _env_int("BLACKJACK_CV_LABEL_SWITCH_STREAK", 2)
CAPTURE_SAMPLE_INTERVAL = _env_float("BLACKJACK_CV_CAPTURE_INTERVAL", 0.1)
CAPTURE_CONSECUTIVE_REQUIRED = _env_int("BLACKJACK_CV_CAPTURE_CONSECUTIVE", 5)
CAPTURE_AVG_CONF = _env_float("BLACKJACK_CV_CAPTURE_AVG_CONF", 0.6)
DEBUG_LOG_EVERY_N = _env_int("BLACKJACK_CV_DEBUG_LOG_EVERY_N", 20)


class DetectorService:
    def __init__(self):
        self._model = None
        self._model_loaded = False
        self._detection_history = deque(maxlen=HISTORY_LENGTH)
        self._clear_streak = 0
        self._last_published_label = None
        self._last_published_conf = 0.0
        self._pending_switch_label = None
        self._pending_switch_streak = 0
        self._tick = 0
        self._last_log_tick = -1

    def load_model(self):
        if not os.path.exists(MODEL_PATH):
            print(f"[Detector] WARNING: Model file not found at {MODEL_PATH}.")
            self._model_loaded = False
            return
        try:
            self._model = YOLO(MODEL_PATH)
            self._model_loaded = True
            print("[Detector] Model loaded successfully.")
        except Exception as e:
            print(f"[Detector] Failed to load model: {e}")
            self._model_loaded = False
        print(
            f"[Detector] Pipeline: UNMIRROR_FOR_INFERENCE={UNMIRROR_FOR_INFERENCE} "
            f"MIRROR_PREVIEW={MIRROR_PREVIEW}"
        )

    def is_model_loaded(self):
        return self._model_loaded

    def get_pipeline_settings(self):
        return {
            "unmirror_for_inference": UNMIRROR_FOR_INFERENCE,
            "mirror_preview": MIRROR_PREVIEW,
            "inference_min_conf": INFERENCE_MIN_CONF,
            "stable_avg_conf": STABLE_AVG_CONF,
            "window_frames": WINDOW_FRAMES,
            "min_agree": MIN_AGREE,
        }

    def _horizontal_flip(self, bgr):
        return cv2.flip(bgr, 1)

    def split_preview_and_inference(self, raw_bgr):
        infer = self._horizontal_flip(raw_bgr) if UNMIRROR_FOR_INFERENCE else raw_bgr
        preview = self._horizontal_flip(raw_bgr) if MIRROR_PREVIEW else raw_bgr
        return preview, infer

    def _run_inference(self, infer_bgr):
        if not self._model_loaded or self._model is None:
            return None, 0.0
        results = self._model(
            infer_bgr, verbose=False, conf=INFERENCE_MIN_CONF,
            iou=YOLO_IOU, max_det=YOLO_MAX_DET,
        )
        best_label = None
        best_conf = 0.0
        for result in results:
            if result.boxes is None or len(result.boxes) == 0:
                continue
            for box in result.boxes:
                conf = float(box.conf[0])
                if conf < INFERENCE_MIN_CONF:
                    continue
                cls_id = int(box.cls[0])
                label = result.names[cls_id]
                if conf > best_conf:
                    best_conf = conf
                    best_label = label
        if best_label is not None:
            normalized = normalize_card_label(best_label)
            if normalized is not None:
                best_label = normalized
        return best_label, best_conf

    def _frame_to_base64(self, preview_bgr):
        _, buffer = cv2.imencode(".jpg", preview_bgr, [cv2.IMWRITE_JPEG_QUALITY, 82])
        return base64.b64encode(buffer).decode("utf-8")

    def _candidate_from_recent_window(self):
        window = list(self._detection_history)[-WINDOW_FRAMES:]
        valid = [(lbl, c) for lbl, c in window if lbl is not None]
        if len(valid) < MIN_AGREE:
            return None, 0.0, "not_enough_detections"
        counter = Counter(lbl for lbl, _ in valid)
        label, count = counter.most_common(1)[0]
        if count < MIN_AGREE:
            return None, 0.0, "insufficient_agreement"
        confs = [c for lbl, c in valid if lbl == label]
        avg_conf = sum(confs) / len(confs)
        if avg_conf < STABLE_AVG_CONF:
            return None, 0.0, "avg_conf_below_stable"
        return label, avg_conf, "ok"

    def _apply_label_switch_lock(self, candidate_label, candidate_conf):
        if candidate_label is None:
            return None, 0.0
        if self._last_published_label is None:
            return candidate_label, candidate_conf
        if candidate_label == self._last_published_label:
            self._pending_switch_label = None
            self._pending_switch_streak = 0
            return candidate_label, candidate_conf
        if candidate_label == self._pending_switch_label:
            self._pending_switch_streak += 1
        else:
            self._pending_switch_label = candidate_label
            self._pending_switch_streak = 1
        if self._pending_switch_streak >= LABEL_SWITCH_STREAK:
            self._pending_switch_label = None
            self._pending_switch_streak = 0
            return candidate_label, candidate_conf
        return self._last_published_label, self._last_published_conf

    def _apply_clear_hysteresis(self, stable_label, stable_conf):
        if stable_label is not None:
            self._clear_streak = 0
            self._last_published_label = stable_label
            self._last_published_conf = stable_conf
            return stable_label, stable_conf
        self._clear_streak += 1
        if self._clear_streak >= CLEAR_STREAK:
            self._last_published_label = None
            self._last_published_conf = 0.0
            self._pending_switch_label = None
            self._pending_switch_streak = 0
            return None, 0.0
        if self._last_published_label is not None:
            return self._last_published_label, self._last_published_conf
        return None, 0.0

    def _debug_log(self, raw_best, raw_conf, stable_reason, locked_label,
                   locked_conf, final_label, final_conf):
        if DEBUG_LOG_EVERY_N <= 0:
            return
        if self._tick - self._last_log_tick < DEBUG_LOG_EVERY_N:
            return
        self._last_log_tick = self._tick
        logger.info(
            "tick=%s | raw=%s/%.3f | window=%s | locked=%s/%.3f | out=%s/%.3f",
            self._tick, raw_best, raw_conf, stable_reason,
            locked_label, locked_conf, final_label, final_conf,
        )

    def get_latest_frame_data(self):
        raw = camera_service.get_latest_frame()
        if raw is None:
            return {"frame": None, "detected_card": None, "confidence": 0.0}
        self._tick += 1
        preview_bgr, infer_bgr = self.split_preview_and_inference(raw)
        label, conf = self._run_inference(infer_bgr)
        raw_best, raw_conf = label, conf
        if label is not None and conf >= INFERENCE_MIN_CONF:
            self._detection_history.append((label, conf))
        else:
            self._detection_history.append((None, 0.0))
        cand_label, cand_conf, stable_reason = self._candidate_from_recent_window()
        locked_label, locked_conf = self._apply_label_switch_lock(cand_label, cand_conf)
        prev_published = self._last_published_label
        final_label, final_conf = self._apply_clear_hysteresis(locked_label, locked_conf)
        self._debug_log(raw_best, raw_conf, stable_reason, locked_label,
                        locked_conf, final_label, final_conf)
        if final_label != prev_published:
            logger.info(
                "output_change | %s -> %s conf=%.3f",
                prev_published, final_label, final_conf,
            )
        return {
            "frame": self._frame_to_base64(preview_bgr),
            "detected_card": final_label,
            "confidence": round(final_conf, 4),
            "pipeline": {
                "unmirror_for_inference": UNMIRROR_FOR_INFERENCE,
                "mirror_preview": MIRROR_PREVIEW,
            },
        }

    def current_card_in_view(self):
        """Single-frame check without touching rolling state."""
        raw = camera_service.get_latest_frame()
        if raw is None:
            return None
        _, infer_bgr = self.split_preview_and_inference(raw)
        lbl, conf = self._run_inference(infer_bgr)
        if lbl and conf >= INFERENCE_MIN_CONF:
            return lbl
        return None

    def capture_stable_card(self, duration_seconds=30):
        """
        Event-driven capture: accepts a card as soon as it appears
        consistently for CAPTURE_CONSECUTIVE_REQUIRED frames in a row.
        duration_seconds is now a max timeout, not a fixed window.
        """
        print(f"[Detector] Waiting for stable card (timeout={duration_seconds}s)...")
        consecutive = 0
        last_label = None
        confs = []
        deadline = time.time() + duration_seconds

        while time.time() < deadline:
            raw = camera_service.get_latest_frame()
            if raw is not None:
                _, infer_bgr = self.split_preview_and_inference(raw)
                lbl, conf = self._run_inference(infer_bgr)
                if lbl and conf >= INFERENCE_MIN_CONF:
                    if lbl == last_label:
                        consecutive += 1
                        confs.append(conf)
                        if consecutive >= CAPTURE_CONSECUTIVE_REQUIRED:
                            avg_conf = sum(confs) / len(confs)
                            if avg_conf >= CAPTURE_AVG_CONF:
                                print(f"[Detector] Stable card: {lbl} ({avg_conf:.2f})")
                                return {"card": lbl, "confidence": round(avg_conf, 4)}
                            else:
                                consecutive = 0
                                last_label = None
                                confs = []
                    else:
                        last_label = lbl
                        consecutive = 1
                        confs = [conf]
                else:
                    consecutive = 0
                    last_label = None
                    confs = []
            time.sleep(CAPTURE_SAMPLE_INTERVAL)

        logger.warning("capture_stable_card: timed out after %ss", duration_seconds)
        return None

    def clear_history(self):
        self._detection_history.clear()
        self._clear_streak = 0
        self._last_published_label = None
        self._last_published_conf = 0.0
        self._pending_switch_label = None
        self._pending_switch_streak = 0


detector_service = DetectorService()