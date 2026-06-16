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
                              QPushButton, QCheckBox, QFrame,
                              QProgressBar)
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
    """Animated emotion score bars with smooth EMA-driven rendering."""

    def __init__(self):
        super().__init__()
        self.scores = {e: 0.0 for e in EMOTIONS}
        self.setFixedSize(250, 330)

    def update_scores(self, scores: dict):
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
            r, g, b = int(hex_c[0:2], 16), int(hex_c[2:4], 16), int(hex_c[4:6], 16)

            # Background track
            painter.setBrush(QBrush(QColor(30, 30, 60)))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(0, y, BAR_W, BAR_H, 4, 4)

            # Fill
            fill_w = int((score / 100) * BAR_W)
            if fill_w > 0:
                painter.setBrush(QBrush(QColor(r, g, b, 200)))
                painter.drawRoundedRect(0, y, fill_w, BAR_H, 4, 4)

            # Labels
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
            painter.drawText(5, y + BAR_H - 9, em.capitalize())
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(BAR_W - 38, y + BAR_H - 9, f"{score:.0f}%")


class HistoryWidget(QWidget):
    """Timeline of confirmed mood detections."""

    def __init__(self):
        super().__init__()
        self.history = []

    def update_history(self, history: list):
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
            r, g, b = int(hex_c[0:2], 16), int(hex_c[2:4], 16), int(hex_c[4:6], 16)
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
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎵 Mood Music Player - by Ronit Gulia")
        self.setFixedSize(1200, 720)
        self.setStyleSheet("background-color: #0d1117; color: #c9d1d9; font-family: 'Segoe UI';")

        self.music = MusicManager()
        self.logger = MoodLogger()
        self.engine = EmotionEngine(on_confirmed=self._on_confirmed)
        self.voice_enabled = VOICE_ENABLED and TTS_AVAILABLE
        self._voice_checked = self.voice_enabled
        self._tts_lock = threading.Lock()
        self._prev_confidence: float = 0.0

        self.cap = cv2.VideoCapture(0)
        self._camera_lock = threading.Lock()
        self._latest_frame = None
        self._camera_running = True
        self._camera_thread = threading.Thread(target=self._camera_worker, daemon=True)
        self._camera_thread.start()

        self._build_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self._loop)
        self.timer.start(30)   # ~33 fps

    # ── UI Construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Title bar ─────────────────────────────────────────────────────────
        title_bar = QWidget()
        title_bar.setFixedHeight(52)
        title_bar.setStyleSheet("background-color: #161b22; border-bottom: 1px solid #30363d;")
        tl = QHBoxLayout(title_bar)
        title_lbl = QLabel("🎵 MOOD MUSIC PLAYER - by Ronit Gulia")
        title_lbl.setFont(QFont("Segoe UI", 15, QFont.Bold))
        title_lbl.setStyleSheet("color: #bd93f9; border: none;")
        title_lbl.setAlignment(Qt.AlignCenter)
        tl.addWidget(title_lbl)
        main_layout.addWidget(title_bar)

        # ── Content row ───────────────────────────────────────────────────────
        content = QWidget()
        content.setStyleSheet("background-color: #0d1117;")
        row = QHBoxLayout(content)
        row.setContentsMargins(15, 10, 15, 10)
        row.setSpacing(12)

        # LEFT: Camera feed
        left_frame = QFrame()
        left_frame.setStyleSheet(
            "background-color: #161b22; border-radius: 8px; border: 1px solid #30363d;"
        )
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

        # MIDDLE: Emotion scores + controls
        mid_frame = QFrame()
        mid_frame.setFixedWidth(290)
        mid_frame.setStyleSheet(
            "background-color: #161b22; border-radius: 8px; border: 1px solid #30363d;"
        )
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

        # Vote progress bar (new)
        vote_hdr = QLabel("Confirmation window:")
        vote_hdr.setFont(QFont("Segoe UI", 8))
        vote_hdr.setStyleSheet("color: #555; border: none; margin-top: 4px;")
        mid_layout.addWidget(vote_hdr)

        self.vote_bar = QProgressBar()
        self.vote_bar.setRange(0, 100)
        self.vote_bar.setValue(0)
        self.vote_bar.setTextVisible(False)
        self.vote_bar.setFixedHeight(6)
        self.vote_bar.setStyleSheet("""
            QProgressBar { background-color: #21262d; border-radius: 3px; border: none; }
            QProgressBar::chunk { background-color: #bd93f9; border-radius: 3px; }
        """)
        mid_layout.addWidget(self.vote_bar)

        self.status_lbl = QLabel("Starting...")
        self.status_lbl.setFont(QFont("Segoe UI", 9))
        self.status_lbl.setStyleSheet("color: #555; border: none;")
        self.status_lbl.setAlignment(Qt.AlignCenter)
        self.status_lbl.setWordWrap(True)
        mid_layout.addWidget(self.status_lbl)

        self.voice_cb = QCheckBox("🔊 Voice announcements")
        self.voice_cb.setChecked(self.voice_enabled)
        self.voice_cb.stateChanged.connect(self._on_voice_cb_changed)
        self.voice_cb.setStyleSheet(
            "color: #8b949e; font-family: 'Segoe UI'; font-size: 10pt; border: none;"
        )
        mid_layout.addWidget(self.voice_cb, alignment=Qt.AlignCenter)
        mid_layout.addStretch()
        row.addWidget(mid_frame)

        # RIGHT: History timeline
        right_frame = QFrame()
        right_frame.setStyleSheet(
            "background-color: #161b22; border-radius: 8px; border: 1px solid #30363d;"
        )
        right_layout = QVBoxLayout(right_frame)
        hist_hdr = QLabel("📈 MOOD HISTORY")
        hist_hdr.setFont(QFont("Segoe UI", 10, QFont.Bold))
        hist_hdr.setStyleSheet("color: #8b949e; border: none; padding: 4px;")
        right_layout.addWidget(hist_hdr)
        self.hist_widget = HistoryWidget()
        right_layout.addWidget(self.hist_widget, stretch=1)
        row.addWidget(right_frame, stretch=1)
        main_layout.addWidget(content, stretch=1)

        # ── Bottom status bar ─────────────────────────────────────────────────
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
            "QPushButton:hover { background-color: #9d73d9; }"
        )
        quit_btn.clicked.connect(self._quit)
        bot_layout.addWidget(quit_btn)
        main_layout.addWidget(bot)

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _on_voice_cb_changed(self, state):
        self._voice_checked = (state == Qt.Checked)

    def _on_confirmed(self, emotion: str, confidence: float, scores: dict):
        success, _ = self.music.try_play(emotion)
        if success:
            self.logger.log(emotion, confidence)
            if self._voice_checked and TTS_AVAILABLE:
                self._speak(f"You look {emotion}. Playing music for you.")

    def _speak(self, text: str):
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

    # ── Camera Worker ─────────────────────────────────────────────────────────

    def _camera_worker(self):
        import time
        while self._camera_running:
            ret, frame = self.cap.read()
            if ret:
                with self._camera_lock:
                    self._latest_frame = frame.copy()
            else:
                time.sleep(0.01)

    # ── Main GUI loop (30 fps) ────────────────────────────────────────────────

    def _loop(self):
        with self._camera_lock:
            frame = self._latest_frame
        if frame is None:
            return
        frame = frame.copy()

        self.engine.maybe_analyze(frame)
        latest = self.engine.latest

        # Draw face box + label on frame
        box = latest.get("face_box")
        if box:
            x, y, w, h = box
            hex_c = EMOTION_COLORS.get(latest["dominant"], "#ffffff").lstrip("#")
            r, g, b = int(hex_c[0:2], 16), int(hex_c[2:4], 16), int(hex_c[4:6], 16)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (b, g, r), 2)
            cv2.putText(frame, latest["dominant"], (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (b, g, r), 2)

        # Camera feed
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb = cv2.resize(rgb, (480, 360))
        h2, w2, ch = rgb.shape
        qimg = QImage(rgb.data, w2, h2, ch * w2, QImage.Format_RGB888)
        self.cam_label.setPixmap(QPixmap.fromImage(qimg))

        # Emotion bars & label
        self.bar_widget.update_scores(latest.get("scores", {}))
        dom = latest["dominant"]
        conf = latest["confidence"]
        color = EMOTION_COLORS.get(dom, "#ffffff")
        self.emotion_lbl.setText(
            dom.upper() if dom not in ("detecting...", "No face") else dom
        )
        self.emotion_lbl.setStyleSheet(f"color: {color}; border: none;")

        # Confidence with trend arrow
        trend = ""
        if conf > self._prev_confidence + 1:
            trend = " ▲"
        elif conf < self._prev_confidence - 1:
            trend = " ▼"
        self._prev_confidence = conf
        self.conf_lbl.setText(
            f"Confidence: {conf:.0f}%{trend}" if conf > 0 else "Confidence: —"
        )

        # Vote window progress bar
        self.vote_bar.setValue(latest.get("vote_fill", 0))

        # Status & history
        self.status_lbl.setText(latest.get("status", ""))
        self.hist_widget.update_history(self.logger.get_history())

        # Bottom bar
        if self.music.current_mood:
            self.song_lbl.setText(f"🎵 Last played for: {self.music.current_mood}")
        cd = self.music.time_until_next()
        self.cd_lbl.setText(f"⏱ Next song in {cd}s" if cd > 0 else "✅ Ready")

    # ── Graceful shutdown ─────────────────────────────────────────────────────

    def _quit(self):
        self.timer.stop()
        self._camera_running = False
        self.engine.shutdown()      # Gracefully stop thread pool
        self.logger.flush()         # Flush any buffered log entries
        if self._camera_thread.is_alive():
            self._camera_thread.join(timeout=1.0)
        self.cap.release()
        self.close()

    def closeEvent(self, event):
        """Also handle window close button (×)."""
        self.timer.stop()
        self._camera_running = False
        self.engine.shutdown()
        self.logger.flush()
        if self._camera_thread.is_alive():
            self._camera_thread.join(timeout=1.0)
        self.cap.release()
        event.accept()


def run():
    app = QApplication(sys.argv)
    window = MoodMusicApp()
    window.show()
    sys.exit(app.exec_())