# ─────────────────────────────────────────────
# Mood Music Player
# Author: Ronit Gulia
# GitHub: https://github.com/ronitgulia
# Date: April 2026
# Description: Detects facial emotions using OpenCV DNN (SSD face detector + FER+ ONNX)
# ─────────────────────────────────────────────

import cv2
import numpy as np
import os
import urllib.request
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from collections import deque
from config import (
    CONFIDENCE_THRESHOLD, ANALYSIS_INTERVAL,
    SMOOTHING_ALPHA, VOTE_WINDOW, VOTE_THRESHOLD,
)

# ── Emotion ONNX model ────────────────────────────────────────────────────────
MODEL_URL = (
    "https://github.com/onnx/models/raw/main/validated/"
    "vision/body_analysis/emotion_ferplus/model/emotion-ferplus-8.onnx"
)
MODEL_PATH = "emotion_model.onnx"

# ── OpenCV DNN SSD face detector ──────────────────────────────────────────────
# Detects faces at angles, in low light, and partial/profile views —
# far superior to Haar cascades.
FACE_PROTO_URL = (
    "https://raw.githubusercontent.com/opencv/opencv/master/"
    "samples/dnn/face_detector/opencv_face_detector.pbtxt"
)
FACE_MODEL_URL = (
    "https://github.com/opencv/opencv_3rdparty/raw/"
    "dnn_samples_face_detector_20170830/opencv_face_detector_uint8.pb"
)
FACE_PROTO_PATH = "face_detector.pbtxt"
FACE_MODEL_PATH = "face_detector.pb"

# ── FER+ label mapping ────────────────────────────────────────────────────────
FER_LABELS = ["neutral", "happiness", "surprise", "sadness",
              "anger", "disgust", "fear", "contempt"]

EMOTIONS = ["happy", "sad", "angry", "neutral", "surprise", "fear", "disgust"]

LABEL_MAP = {
    "neutral":   "neutral",
    "happiness": "happy",
    "surprise":  "surprise",
    "sadness":   "sad",
    "anger":     "angry",
    "disgust":   "disgust",
    "fear":      "fear",
    "contempt":  "contempt",   # Kept distinct; blended below
}


def _download_file(url: str, path: str, label: str) -> None:
    """Download a file if it doesn't already exist locally."""
    if not os.path.exists(path):
        print(f"📥 Downloading {label}...")
        try:
            urllib.request.urlretrieve(url, path)
            print(f"✅ {label} downloaded!")
        except Exception as e:
            print(f"❌ Failed to download {label}: {e}")
            raise


class EmotionEngine:
    """
    Emotion detection pipeline:
      1. OpenCV DNN SSD face detector  — angle/lighting robust
      2. FER+ ONNX model               — 8-class emotion scores
      3. EMA temporal smoothing        — eliminates jitter
      4. Voting-window confirmation    — noise-resistant triggering
    """

    def __init__(self, on_confirmed):
        self.on_confirmed = on_confirmed
        self._analyzing = False
        self._lock = threading.Lock()
        self._vote_window: deque = deque(maxlen=VOTE_WINDOW)
        self._last_time: float = 0.0
        self._smoothed_scores: dict = {e: 0.0 for e in EMOTIONS}

        # ThreadPoolExecutor — reuses threads, no per-frame spawn overhead
        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="emotion")

        # CLAHE — far better than equalizeHist for webcam/uneven lighting
        self._clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

        self.latest: dict = {
            "dominant": "detecting...",
            "scores": {e: 0.0 for e in EMOTIONS},
            "confidence": 0.0,
            "face_box": None,
            "status": "Ready! Show your face 😊",
            "vote_fill": 0,     # 0-100, used by GUI progress bar
        }

        # Download & load models
        _download_file(MODEL_URL, MODEL_PATH, "Emotion ONNX model")
        _download_file(FACE_PROTO_URL, FACE_PROTO_PATH, "Face detector config")
        _download_file(FACE_MODEL_URL, FACE_MODEL_PATH, "Face detector model")

        self._net = cv2.dnn.readNetFromONNX(MODEL_PATH)
        self._face_net = cv2.dnn.readNetFromTensorflow(FACE_MODEL_PATH, FACE_PROTO_PATH)

        print("✅ Emotion engine ready!")

    # ── Public API ────────────────────────────────────────────────────────────

    def maybe_analyze(self, frame: np.ndarray) -> None:
        """Called every GUI tick. Submits analysis job if interval elapsed."""
        now = time.time()
        with self._lock:
            if self._analyzing:
                return
            if now - self._last_time < ANALYSIS_INTERVAL:
                return
            self._analyzing = True
            self._last_time = now
        self._executor.submit(self._analyze, frame.copy())

    def shutdown(self) -> None:
        """Gracefully shut down the thread pool (call on app close)."""
        self._executor.shutdown(wait=False)

    # ── Internal ──────────────────────────────────────────────────────────────

    def _detect_faces(self, frame: np.ndarray) -> list:
        """
        OpenCV DNN SSD face detector.
        Returns list of (x, y, w, h, det_confidence) tuples.
        Works at angles, partial occlusion, variable lighting.
        """
        h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)),
            scalefactor=1.0,
            size=(300, 300),
            mean=(104.0, 177.0, 123.0),
        )
        self._face_net.setInput(blob)
        dets = self._face_net.forward()

        faces = []
        for i in range(dets.shape[2]):
            det_conf = float(dets[0, 0, i, 2])
            if det_conf < 0.50:
                continue
            box = dets[0, 0, i, 3:7] * np.array([w, h, w, h])
            x1, y1, x2, y2 = box.astype(int)
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            if x2 > x1 and y2 > y1:
                faces.append((x1, y1, x2 - x1, y2 - y1, det_conf))
        return faces

    def _preprocess_face(self, frame: np.ndarray, x: int, y: int,
                         w: int, h: int) -> np.ndarray:
        """
        Crop face with padding, apply CLAHE, resize to 64×64 for FER+ model.
        CLAHE (Contrast Limited Adaptive Histogram Equalization) dramatically
        improves accuracy for webcam frames with uneven/backlit lighting.
        """
        pad = int(max(w, h) * 0.12)
        x1 = max(0, x - pad)
        y1 = max(0, y - pad)
        x2 = min(frame.shape[1], x + w + pad)
        y2 = min(frame.shape[0], y + h + pad)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = self._clahe.apply(gray)
        roi = gray[y1:y2, x1:x2]
        roi = cv2.resize(roi, (64, 64))
        return roi

    def _run_emotion_model(self, face_roi: np.ndarray) -> np.ndarray:
        """Run FER+ ONNX model, return softmax probabilities (8 classes)."""
        blob = cv2.dnn.blobFromImage(face_roi, scalefactor=1.0, size=(64, 64))
        self._net.setInput(blob)
        raw = self._net.forward()[0]
        shifted = raw - raw.max()
        exp_v = np.exp(shifted)
        return exp_v / exp_v.sum()

    def _build_scores(self, probs: np.ndarray) -> dict:
        """
        Map FER+ 8-class probabilities → our 7 emotions.
        contempt is blended: 60% into disgust, 40% into neutral.
        This preserves information instead of silently discarding it.
        """
        scores = {e: 0.0 for e in EMOTIONS}
        contempt_prob = 0.0

        for i, fer_label in enumerate(FER_LABELS):
            mapped = LABEL_MAP.get(fer_label, "neutral")
            val = float(probs[i]) * 100.0
            if mapped == "contempt":
                contempt_prob = val
            else:
                scores[mapped] = max(scores[mapped], val)

        # Blend contempt signal into related emotions
        scores["disgust"] = min(100.0, scores["disgust"] + contempt_prob * 0.60)
        scores["neutral"] = min(100.0, scores["neutral"] + contempt_prob * 0.40)
        return scores

    def _apply_ema(self, raw_scores: dict) -> dict:
        """
        Exponential Moving Average smoothing across frames.
        Eliminates single-frame spikes and jittery emotion labels.
        α=SMOOTHING_ALPHA: higher = more reactive, lower = smoother.
        """
        alpha = SMOOTHING_ALPHA
        for e in EMOTIONS:
            self._smoothed_scores[e] = (
                alpha * raw_scores[e] + (1.0 - alpha) * self._smoothed_scores[e]
            )
        return dict(self._smoothed_scores)

    def _decay_scores(self) -> None:
        """Gently decay scores toward zero when no face is detected."""
        for e in EMOTIONS:
            self._smoothed_scores[e] *= 0.80

    def _check_vote_window(self, dominant: str, confidence: float) -> None:
        """
        Voting-window confirmation:
        An emotion is only confirmed when it wins ≥ VOTE_THRESHOLD of the
        last VOTE_WINDOW frames. Much more robust than a raw consecutive count.
        """
        self._vote_window.append(dominant)
        fill_pct = int(len(self._vote_window) / VOTE_WINDOW * 100)

        with self._lock:
            self.latest["vote_fill"] = fill_pct

        if len(self._vote_window) < VOTE_WINDOW:
            self.latest["status"] = (
                f"Sampling... [{len(self._vote_window)}/{VOTE_WINDOW}]"
            )
            return

        # Tally votes
        tally: dict = {}
        for vote in self._vote_window:
            tally[vote] = tally.get(vote, 0) + 1

        top = max(tally, key=tally.get)
        ratio = tally[top] / VOTE_WINDOW

        if ratio >= VOTE_THRESHOLD:
            self._vote_window.clear()
            with self._lock:
                self.latest["status"] = (
                    f"✓ Confirmed: {top} ({int(ratio * 100)}% votes)"
                )
            threading.Thread(
                target=self.on_confirmed,
                args=(top, confidence, dict(self._smoothed_scores)),
                daemon=True,
            ).start()
        else:
            pct = int(ratio * 100)
            need = int(VOTE_THRESHOLD * 100)
            with self._lock:
                self.latest["status"] = (
                    f"Sensing '{top}'... ({pct}% — need {need}%)"
                )

    def _analyze(self, frame: np.ndarray) -> None:
        """Core analysis pipeline — runs in thread pool worker."""
        try:
            faces = self._detect_faces(frame)

            if not faces:
                with self._lock:
                    self.latest["status"] = "No face detected — check lighting!"
                    self.latest["face_box"] = None
                    self._decay_scores()
                    self.latest["scores"] = dict(self._smoothed_scores)
                return

            # Pick largest detected face
            x, y, w, h, _ = max(faces, key=lambda f: f[2] * f[3])

            # Preprocess → emotion model → probabilities
            face_roi = self._preprocess_face(frame, x, y, w, h)
            probs = self._run_emotion_model(face_roi)
            raw_scores = self._build_scores(probs)

            # EMA smooth
            smoothed = self._apply_ema(raw_scores)
            dominant = max(smoothed, key=smoothed.get)
            confidence = smoothed[dominant]

            with self._lock:
                self.latest.update({
                    "dominant": dominant,
                    "scores": smoothed,
                    "confidence": confidence,
                    "face_box": (int(x), int(y), int(w), int(h)),
                })

            # Low confidence — reset vote window
            if confidence < CONFIDENCE_THRESHOLD:
                with self._lock:
                    self.latest["status"] = (
                        f"Low confidence ({confidence:.0f}%) — keep still"
                    )
                self._vote_window.clear()
                return

            # Voting window confirmation
            self._check_vote_window(dominant, confidence)

        except Exception as e:
            with self._lock:
                self.latest["status"] = f"Error: {str(e)[:60]}"
                self.latest["face_box"] = None
        finally:
            with self._lock:
                self._analyzing = False