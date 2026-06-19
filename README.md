<div align="center">

# 🎵 Mood Music Player

### Real-time emotion detection that plays music matching your mood

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-5C3EE8?style=flat-square&logo=opencv&logoColor=white)](https://opencv.org)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15-41CD52?style=flat-square&logo=qt&logoColor=white)](https://riverbankcomputing.com/software/pyqt)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

*Built by [Ronit Gulia](https://github.com/ronitgulia)*

</div>

---

## 📖 What is this?

Mood Music Player watches your face through your webcam in real time, detects your current emotional state using a deep learning model, and automatically opens a matching YouTube playlist — all without you lifting a finger.

Point the camera at your face. The app does the rest.

---

## ✨ Features

- 🎯 **7 emotions detected** — happy, sad, angry, neutral, surprise, fear, disgust
- 🧠 **OpenCV DNN face detector** — works at angles, in low light, and with partial faces (far more robust than classic Haar cascades)
- 📊 **EMA temporal smoothing** — eliminates jittery/flickering emotion labels between frames
- 🗳️ **Voting-window confirmation** — an emotion is only acted on when it wins 60%+ of 8 consecutive frames, preventing false triggers
- 🎨 **CLAHE preprocessing** — handles backlit rooms and uneven webcam lighting gracefully
- ⏱️ **Per-emotion cooldowns** — surprise triggers sooner (60s), neutral waits longer (180s)
- ⚡ **Instant mood-shift override** — a strong emotion change (e.g. neutral → angry) bypasses the cooldown immediately
- 📝 **Mood history log** — all detections saved to `mood_log.csv` with buffered I/O
- 🔊 **Optional voice announcements** — announces detected mood out loud via pyttsx3

---

## 🛠️ Tech Stack

| Layer | Technology |  
|---|---|
| Language | Python 3.10+ |
| Face Detection | OpenCV DNN (SSD ResNet, TensorFlow) |
| Emotion Model | FER+ ONNX (8-class, via OpenCV DNN) |
| GUI Framework | PyQt5 |
| Preprocessing | CLAHE (Contrast Limited Adaptive Histogram Equalization) |
| Smoothing | Exponential Moving Average (EMA, α=0.35) |
| Confirmation | Rolling voting window (8 frames, 60% threshold) |
| Voice | pyttsx3 (offline TTS) |
| Logging | Buffered CSV writer |
| Threading | `concurrent.futures.ThreadPoolExecutor` |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or newer
- A working webcam
- Internet connection (first run only — downloads model files automatically)

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/ronitgulia/Mood_Music.git
cd Mood_Music

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python main.py
```

> **First run:** The app will automatically download two model files (~42 MB total) — the FER+ emotion model and the OpenCV DNN face detector. This only happens once. After that, startup is instant.

---

## 🎭 Emotions & Music

| Emotion | Color | Music Vibe | Cooldown |
|---|---|---|---|
| 😊 Happy | Gold | Upbeat / Bhangra | 120s |
| 😢 Sad | Blue | Calm / Melodic | 150s |
| 😠 Angry | Red | Energetic / Intense | 90s |
| 😐 Neutral | Grey | Lo-fi / Chill | 180s |
| 😲 Surprise | Pink | Dramatic / Energetic | 60s |
| 😨 Fear | Purple | Devotional / Calming | 120s |
| 🤢 Disgust | Green | Soft / Romantic | 120s |

---

## 🏗️ Project Structure

```
Mood_Music/
│
├── main.py             # Entry point — run this
├── gui.py              # PyQt5 main window, live camera feed, all UI widgets
├── emotion_engine.py   # Face detection + emotion inference pipeline
│                       #   └─ DNN face detector → CLAHE → FER+ ONNX → EMA → voting
├── music_manager.py    # Per-emotion cooldowns, mood-shift bypass, YouTube opener
├── mood_logger.py      # Buffered CSV mood history logger
├── config.py           # All tunable settings, emotion colours, song library
└── requirements.txt    # Python dependencies
```

---

## ⚙️ Configuration

All behaviour can be tuned in [`config.py`](config.py):

```python
CONFIDENCE_THRESHOLD = 40     # Min smoothed confidence (%) to accept a result
ANALYSIS_INTERVAL    = 0.35   # Seconds between analysis frames
SMOOTHING_ALPHA      = 0.35   # EMA weight (higher = more reactive)
VOTE_WINDOW          = 8      # Frames in the confirmation window
VOTE_THRESHOLD       = 0.60   # Fraction of votes needed to confirm
```

---

## 🔬 How the Detection Pipeline Works

```
Webcam frame (30fps)
       │
       ▼ every 0.35s
┌─────────────────────────┐
│  OpenCV DNN Face Detect │  ← SSD ResNet, detects faces at any angle
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  CLAHE Preprocessing    │  ← Fixes uneven/backlit lighting
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  FER+ ONNX Model        │  ← 8-class emotion probabilities
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  EMA Smoothing (α=0.35) │  ← Removes single-frame noise/jitter
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  Voting Window (8 frames│  ← Confirms only when 60%+ agree
│  / 60% threshold)       │
└────────────┬────────────┘
             │
             ▼
      🎵 Open YouTube
```

---

## 👨‍💻 Author 

**Ronit Gulia**
- GitHub: [@ronitgulia](https://github.com/ronitgulia)
- Project: [Mood Music Player](https://github.com/ronitgulia/Mood_Music)

---

<div align="center">
  <sub>Made with ❤️ and a lot of facial expressions</sub>
</div>
