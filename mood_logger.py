# ─────────────────────────────────────────────
# Mood Music Player
# Author: Ronit Gulia
# GitHub: https://github.com/ronitgulia
# Date: April 2026
# Description: Logs mood detection history to CSV file
# ─────────────────────────────────────────────

import csv
import os
from datetime import datetime
from config import MOOD_LOG_FILE, HISTORY_DISPLAY

class MoodLogger:
    def __init__(self):
        self._file = MOOD_LOG_FILE
        if not os.path.exists(self._file):
            with open(self._file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["time", "emotion", "confidence"])

    def log(self, emotion, confidence):
        with open(self._file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                emotion,
                f"{confidence:.1f}"
            ])

    def get_history(self):
        if not os.path.exists(self._file):
            return []
        with open(self._file, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        return rows[-HISTORY_DISPLAY:]