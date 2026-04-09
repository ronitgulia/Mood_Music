#  Mood Music Player

A real-time emotion-based music recommender built with Python.

The app uses your webcam to detect your facial expression using a
deep learning ONNX model, then automatically opens a YouTube song
matching your mood.

##  Developed By
**Ronit Gulia**
- GitHub: [ronitgulia](https://github.com/ronitgulia)

##  Tech Stack
- Python 3.10+
- OpenCV — face detection and webcam feed
- ONNX via OpenCV DNN — emotion recognition
- PyQt5 — desktop GUI
- pyttsx3 — voice announcements

##  How to Run
git clone https://github.com/ronitgulia/Mood_Music.git
cd Mood_Music
pip install -r requirements.txt
python main.py

##  Emotions Detected
| Emotion    | Music Style      |
|-----------|-----------------|
|  Happy   | Upbeat / Bhangra |
|  Sad     | Calm / Melodic   |
|  Angry   | Energetic        |
|  Neutral | Lo-fi / Chill    |
|  Surprise| Energetic        |
|  Fear    | Devotional       |
|  Disgust | Soft / Romantic  |

##  Project Structure
- main.py — Entry point
- gui.py — PyQt5 GUI window
- emotion_engine.py — ONNX emotion detection
- music_manager.py — YouTube song opener
- mood_logger.py — Logs mood history to CSV
- config.py — All settings and song links
- requirements.txt — All dependencies