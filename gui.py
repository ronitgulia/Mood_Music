# ─────────────────────────────────────────────
# Mood Music Player
# Author: Ronit Gulia
# GitHub: https://github.com/ronitgulia
# Date: April 2026
# Description: Main GUI window using PyQt5
# ─────────────────────────────────────────────

import sys
import cv2
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget,
                              QLabel, QHBoxLayout, QVBoxLayout,
                              QPushButton, QCheckBox, QFrame)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QFont, QColor, QPainter, QPen, QBrush
from config import EMOTION_COLORS, VOICE_ENABLED
from emotion_engine import EmotionEngine
from music_manager import MusicManager
from mood_logger import MoodLogger

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

EMOTIONS = ["happy", "sad", "angry", "neutral", "surprise", "fear", "disgust"]

class BarWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.scores = {e: 0.0 for e in EMOTIONS}
        self.setFixedSize(250, 330)

    def update_scores(self, scores):
        self.scores = scores
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        BAR_H, BAR_W, GAP = 32, 230, 13
        for i, em in enumerate(EMOTIONS):
            y = i * (BAR_H + GAP) + 8
            score = self.scores.get(em, 0)
            hex_c = EMOTION_COLORS.get(em, "#888888").lstrip("#")
            r,g,b = int(hex_c[0:2],16), int(hex_c[2:4],16), int(hex_c[4:6],16)
            painter.setBrush(QBrush(QColor(30, 30, 60)))
            painter.setPen(Qt.NoPen)
            painter.drawRect(0, y, BAR_W, BAR_H)
            fill_w = int((score / 100) * BAR_W)
            if fill_w > 0:
                painter.setBrush(QBrush(QColor(r, g, b)))
                painter.drawRect(0, y, fill_w, BAR_H)
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
            painter.drawText(5, y + BAR_H - 9, em.capitalize())
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(BAR_W - 35, y + BAR_H - 9, f"{score:.0f}%")

class HistoryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.history = []

    def update_history(self, history):
        self.history = history
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        W = self.width()
        if not self.history:
            painter.setPen(QColor(60, 60, 60))
            painter.setFont(QFont("Segoe UI", 11))
            painter.drawText(self.rect(), Qt.AlignCenter, "No history yet")
            return
        item_h = min(self.height() // max(len(self.history), 1), 40)
        for i, item in enumerate(reversed(self.history)):
            y = i * item_h + 20
            if y > self.height() - 10:
                break
            em = item["emotion"]
            conf = item["confidence"]
            t_str = item["time"].split(" ")[1]
            hex_c = EMOTION_COLORS.get(em, "#888888").lstrip("#")
            r,g,b = int(hex_c[0:2],16), int(hex_c[2:4],16), int(hex_c[4:6],16)
            col = QColor(r, g, b)
            painter.setBrush(QBrush(col))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(10, y - 7, 14, 14)
            painter.setPen(col)
            painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
            painter.drawText(30, y + 5, em.capitalize())
            painter.setPen(QColor(100, 100, 100))
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(130, y + 5, f"{conf}%")
            painter.setPen(QColor(70, 70, 70))
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(W - 70, y + 5, t_str)

class MoodMusicApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎵 Mood Music Player - by Ronit Gulia")
        self.setFixedSize(1200, 700)
        self.setStyleSheet("background-color: #0d1117; color: #c9d1d9; font-family: 'Segoe UI';")
        self.music = MusicManager()
        self.logger = MoodLogger()
        self.engine = EmotionEngine(on_confirmed=self._on_confirmed)
        self.voice_enabled = VOICE_ENABLED and TTS_AVAILABLE
        self._tts_lock = threading.Lock()
        self.cap = cv2.VideoCapture(0)
        self._build_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self._loop)
        self.timer.start(30)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Title bar
        title_bar = QWidget()
        title_bar.setFixedHeight(52)
        title_bar.setStyleSheet("background-color: #161b22; border-bottom: 1px solid #30363d;")
        from PyQt5.QtWidgets import QHBoxLayout
        tl = QHBoxLayout(title_bar)
        title_lbl = QLabel("🎵 MOOD MUSIC PLAYER - by Ronit Gulia")
        title_lbl.setFont(QFont("Segoe UI", 15, QFont.Bold))
        title_lbl.setStyleSheet("color: #bd93f9; border: none;")
        title_lbl.setAlignment(Qt.AlignCenter)
        tl.addWidget(title_lbl)
        main_layout.addWidget(title_bar)

        # Content
        content = QWidget()
        content.setStyleSheet("background-color: #0d1117;")
        row = QHBoxLayout(content)
        row.setContentsMargins(15, 10, 15, 10)
        row.setSpacing(12)

        # LEFT: Camera
        left_frame = QFrame()
        left_frame.setStyleSheet("background-color: #161b22; border-radius: 8px; border: 1px solid #30363d;")
        left_layout = QVBoxLayout(left_frame)
        cam_hdr = QLabel("📷 LIVE FEED")
        cam_hdr.setFont(QFont("Segoe UI", 10, QFont.Bold))
        cam_hdr.setStyleSheet("color: #8b949e; border: none; padding: 4px;")
        left_layout.addWidget(cam_hdr)
        self.cam_label = QLabel()
        self.cam_label.setFixedSize(480, 360)
        self.cam_label.setStyleSheet("background-color: #000; border-radius: 4px;")
        left_layout.addWidget(self.cam_label)
        left_layout.addStretch()
        row.addWidget(left_frame)

        # MIDDLE: Bars
        mid_frame = QFrame()
        mid_frame.setFixedWidth(280)
        mid_frame.setStyleSheet("background-color: #161b22; border-radius: 8px; border: 1px solid #30363d;")
        mid_layout = QVBoxLayout(mid_frame)
        bar_hdr = QLabel("📊 EMOTION SCORES")
        bar_hdr.setFont(QFont("Segoe UI", 10, QFont.Bold))
        bar_hdr.setStyleSheet("color: #8b949e; border: none; padding: 4px;")
        mid_layout.addWidget(bar_hdr)
        self.bar_widget = BarWidget()
        mid_layout.addWidget(self.bar_widget)
        self.emotion_lbl = QLabel("detecting...")
        self.emotion_lbl.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.emotion_lbl.setStyleSheet("color: #FFD700; border: none;")
        self.emotion_lbl.setAlignment(Qt.AlignCenter)
        mid_layout.addWidget(self.emotion_lbl)
        self.conf_lbl = QLabel("Confidence: —")
        self.conf_lbl.setFont(QFont("Segoe UI", 10))
        self.conf_lbl.setStyleSheet("color: #aaa; border: none;")
        self.conf_lbl.setAlignment(Qt.AlignCenter)
        mid_layout.addWidget(self.conf_lbl)
        self.status_lbl = QLabel("Starting...")
        self.status_lbl.setFont(QFont("Segoe UI", 9))
        self.status_lbl.setStyleSheet("color: #555; border: none;")
        self.status_lbl.setAlignment(Qt.AlignCenter)
        self.status_lbl.setWordWrap(True)
        mid_layout.addWidget(self.status_lbl)
        self.voice_cb = QCheckBox("🔊 Voice announcements")
        self.voice_cb.setChecked(self.voice_enabled)
        self.voice_cb.setStyleSheet("color: #8b949e; font-family: 'Segoe UI'; font-size: 10pt; border: none;")
        mid_layout.addWidget(self.voice_cb, alignment=Qt.AlignCenter)
        mid_layout.addStretch()
        row.addWidget(mid_frame)

        # RIGHT: History
        right_frame = QFrame()
        right_frame.setStyleSheet("background-color: #161b22; border-radius: 8px; border: 1px solid #30363d;")
        right_layout = QVBoxLayout(right_frame)
        hist_hdr = QLabel("📈 MOOD HISTORY")
        hist_hdr.setFont(QFont("Segoe UI", 10, QFont.Bold))
        hist_hdr.setStyleSheet("color: #8b949e; border: none; padding: 4px;")
        right_layout.addWidget(hist_hdr)
        self.hist_widget = HistoryWidget()
        right_layout.addWidget(self.hist_widget, stretch=1)
        row.addWidget(right_frame, stretch=1)
        main_layout.addWidget(content, stretch=1)

        # Bottom bar
        bot = QWidget()
        bot.setFixedHeight(44)
        bot.setStyleSheet("background-color: #161b22; border-top: 1px solid #30363d;")
        bot_layout = QHBoxLayout(bot)
        bot_layout.setContentsMargins(15, 0, 15, 0)
        self.song_lbl = QLabel("🎵 No song playing yet")
        self.song_lbl.setFont(QFont("Segoe UI", 10))
        self.song_lbl.setStyleSheet("color: #aaa; border: none;")
        bot_layout.addWidget(self.song_lbl)
        bot_layout.addStretch()
        self.cd_lbl = QLabel("")
        self.cd_lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.cd_lbl.setStyleSheet("color: #bd93f9; border: none;")
        bot_layout.addWidget(self.cd_lbl)
        quit_btn = QPushButton(" QUIT ")
        quit_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        quit_btn.setStyleSheet(
            "QPushButton { background-color: #bd93f9; color: #0d1117; "
            "border: none; padding: 6px 12px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #9d73d9; }")
        quit_btn.clicked.connect(self._quit)
        bot_layout.addWidget(quit_btn)
        main_layout.addWidget(bot)

    def _on_confirmed(self, emotion, confidence, scores):
        success, _ = self.music.try_play(emotion)
        if success:
            self.logger.log(emotion, confidence)
            if self.voice_cb.isChecked() and TTS_AVAILABLE:
                self._speak(f"You look {emotion}. Playing music for you.")

    def _speak(self, text):
        def _do():
            with self._tts_lock:
                try:
                    eng = pyttsx3.init()
                    eng.say(text)
                    eng.runAndWait()
                    eng.stop()
                except Exception:
                    pass
        threading.Thread(target=_do, daemon=True).start()

    def _loop(self):
        ret, frame = self.cap.read()
        if not ret:
            return
        self.engine.maybe_analyze(frame)
        latest = self.engine.latest
        box = latest.get("face_box")
        if box:
            x, y, w, h = box
            hex_c = EMOTION_COLORS.get(latest["dominant"], "#ffffff").lstrip("#")
            r,g,b = int(hex_c[0:2],16), int(hex_c[2:4],16), int(hex_c[4:6],16)
            cv2.rectangle(frame, (x,y), (x+w, y+h), (b,g,r), 2)
            cv2.putText(frame, latest["dominant"], (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.65, (b,g,r), 2)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb = cv2.resize(rgb, (480, 360))
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        self.cam_label.setPixmap(QPixmap.fromImage(qimg))
        self.bar_widget.update_scores(latest.get("scores", {}))
        dom = latest["dominant"]
        conf = latest["confidence"]
        color = EMOTION_COLORS.get(dom, "#ffffff")
        self.emotion_lbl.setText(
            dom.upper() if dom not in ("detecting...", "No face") else dom)
        self.emotion_lbl.setStyleSheet(f"color: {color};")
        self.conf_lbl.setText(f"Confidence: {conf:.0f}%" if conf > 0 else "Confidence: —")
        self.status_lbl.setText(latest.get("status", ""))
        self.hist_widget.update_history(self.logger.get_history())
        if self.music.current_mood:
            self.song_lbl.setText(f"🎵 Last played for: {self.music.current_mood}")
        cd = self.music.time_until_next()
        self.cd_lbl.setText(f"⏱ Next song in {cd}s" if cd > 0 else "✅ Ready")

    def _quit(self):
        self.cap.release()
        self.close()

def run():
    app = QApplication(sys.argv)
    window = MoodMusicApp()
    window.show()
    sys.exit(app.exec_())