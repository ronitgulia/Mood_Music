# ─────────────────────────────────────────────
# Mood Music Player
# Author: Ronit Gulia
# GitHub: https://github.com/ronitgulia
# Date: April 2026
# Description: Detects facial emotions using OpenCV DNN
# ─────────────────────────────────────────────

import cv2
import numpy as np
import os
import urllib.request
import threading
import time
from config import CONFIDENCE_THRESHOLD, CONFIRM_COUNT_NEEDED, ANALYSIS_INTERVAL

MODEL_URL = ("https://github.com/onnx/models/raw/main/validated/"
             "vision/body_analysis/emotion_ferplus/model/emotion-ferplus-8.onnx")
MODEL_PATH = "emotion_model.onnx"

FER_LABELS = ["neutral", "happiness", "surprise", "sadness",
              "anger", "disgust", "fear", "contempt"]

LABEL_MAP = {
    "neutral":   "neutral",
    "happiness": "happy",
    "surprise":  "surprise",
    "sadness":   "sad",
    "anger":     "angry",
    "disgust":   "disgust",
    "fear":      "fear",
    "contempt":  "neutral",
}

def _download_model():
    if not os.path.exists(MODEL_PATH):
        print("📥 Downloading emotion model...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("✅ Model downloaded!")

class EmotionEngine:
    def __init__(self, on_confirmed):
        self.on_confirmed = on_confirmed
        self._analyzing = False
        self._lock = threading.Lock()
        self._confirm_emotion = None
        self._confirm_count = 0
        self._last_time = 0
        self.latest = {
            "dominant": "detecting...",
            "scores": {e: 0.0 for e in
                      ["happy","sad","angry","neutral","surprise","fear","disgust"]},
            "confidence": 0.0,
            "face_box": None,
            "status": "Ready! Show your face 😊",
        }
        _download_model()
        self._net = cv2.dnn.readNetFromONNX(MODEL_PATH)

        # Use 3 cascades for better detection
        self._detector = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self._detector_alt = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_alt.xml"
        )
        self._detector_alt2 = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_alt2.xml"
        )
        print("✅ Emotion engine ready!")

    def maybe_analyze(self, frame):
        now = time.time()
        with self._lock:
            if self._analyzing:
                return
            if now - self._last_time < ANALYSIS_INTERVAL:
                return
            self._analyzing = True
            self._last_time = now
        threading.Thread(target=self._analyze,
                        args=(frame.copy(),), daemon=True).start()

    def _detect_face(self, gray):
        # Try all 3 cascades
        for detector in [self._detector, self._detector_alt, self._detector_alt2]:
            faces = detector.detectMultiScale(
                gray,
                scaleFactor=1.05,
                minNeighbors=3,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            if len(faces) > 0:
                return faces
        return []

    def _analyze(self, frame):
        try:
            # Try both original and flipped frame
            for img in [frame, cv2.flip(frame, 1)]:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # Improve contrast
                gray = cv2.equalizeHist(gray)
                faces = self._detect_face(gray)

                if len(faces) > 0:
                    break

            if len(faces) == 0:
                with self._lock:
                    self.latest["status"] = "No face detected — check lighting!"
                    self.latest["face_box"] = None
                return

            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])

            # Add padding around face
            pad = int(w * 0.1)
            x1 = max(0, x - pad)
            y1 = max(0, y - pad)
            x2 = min(gray.shape[1], x + w + pad)
            y2 = min(gray.shape[0], y + h + pad)

            face_roi = gray[y1:y2, x1:x2]
            face_roi = cv2.resize(face_roi, (64, 64))

            blob = cv2.dnn.blobFromImage(face_roi, 1.0, (64, 64))
            self._net.setInput(blob)
            raw_scores = self._net.forward()[0]

            shifted = raw_scores - raw_scores.max()
            exp_vals = np.exp(shifted)
            probs = exp_vals / exp_vals.sum()

            our_scores = {e: 0.0 for e in
                         ["happy","sad","angry","neutral","surprise","fear","disgust"]}
            for i, fer_label in enumerate(FER_LABELS):
                key = LABEL_MAP.get(fer_label, "neutral")
                our_scores[key] = max(our_scores[key], float(probs[i]) * 100)

            dominant = max(our_scores, key=our_scores.get)
            confidence = our_scores[dominant]

            with self._lock:
                self.latest.update({
                    "dominant": dominant,
                    "scores": our_scores,
                    "confidence": confidence,
                    "face_box": (int(x), int(y), int(w), int(h)),
                })

            if confidence < CONFIDENCE_THRESHOLD:
                self.latest["status"] = (f"Low confidence "
                                        f"({confidence:.0f}%) — ignoring")
                self._confirm_count = 0
                return

            if dominant == self._confirm_emotion:
                self._confirm_count += 1
            else:
                self._confirm_emotion = dominant
                self._confirm_count = 1

            if self._confirm_count >= CONFIRM_COUNT_NEEDED:
                self._confirm_count = 0
                self.latest["status"] = f"✓ Confirmed: {dominant}"
                threading.Thread(
                    target=self.on_confirmed,
                    args=(dominant, confidence, our_scores),
                    daemon=True
                ).start()
            else:
                left = CONFIRM_COUNT_NEEDED - self._confirm_count
                self.latest["status"] = (f"Confirming '{dominant}'..."
                                        f" ({left} more)")

        except Exception as e:
            with self._lock:
                self.latest["status"] = f"Error: {str(e)[:60]}"
                self.latest["face_box"] = None
        finally:
            with self._lock:
                self._analyzing = False