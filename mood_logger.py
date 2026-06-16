# ─────────────────────────────────────────────
# Mood Music Player
# Author: Ronit Gulia
# GitHub: https://github.com/ronitgulia
# Date: April 2026
# Description: Logs mood detection history to CSV file (buffered I/O)
# ─────────────────────────────────────────────

import csv
import os
import threading
from datetime import datetime
from collections import deque
from config import MOOD_LOG_FILE, HISTORY_DISPLAY, LOG_BUFFER_SIZE


class MoodLogger:
    """
    Thread-safe CSV logger with write buffering.
    
    Fix: History is now cached in memory to avoid O(N) disk I/O
    in the UI loop.
    """

    def __init__(self):
        self._file: str = MOOD_LOG_FILE
        self._buffer: list = []
        self._lock = threading.Lock()
        self._history = deque(maxlen=HISTORY_DISPLAY)

        if not os.path.exists(self._file):
            with open(self._file, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(["time", "emotion", "confidence"])
        else:
            with open(self._file, "r", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
                for row in rows[-HISTORY_DISPLAY:]:
                    self._history.append(row)

    # ── Public API ────────────────────────────────────────────────────────────

    def log(self, emotion: str, confidence: float) -> None:
        """Buffer a mood entry. Flushes automatically when buffer is full."""
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conf_str = f"{confidence:.1f}"
        
        row_list = [time_str, emotion, conf_str]
        row_dict = {"time": time_str, "emotion": emotion, "confidence": conf_str}
        
        with self._lock:
            self._buffer.append(row_list)
            self._history.append(row_dict)
            if len(self._buffer) >= LOG_BUFFER_SIZE:
                self._flush_locked()

    def flush(self) -> None:
        """Force-write all buffered entries to disk (call on app close)."""
        with self._lock:
            self._flush_locked()

    def get_history(self) -> list:
        """Return the last HISTORY_DISPLAY mood entries from memory cache."""
        with self._lock:
            return list(self._history)

    # ── Internal ──────────────────────────────────────────────────────────────

    def _flush_locked(self) -> None:
        """Write all buffered rows to CSV. Must be called with self._lock held."""
        if not self._buffer:
            return
        with open(self._file, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows(self._buffer)
        self._buffer.clear()