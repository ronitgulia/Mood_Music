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
from config import MOOD_LOG_FILE, HISTORY_DISPLAY, LOG_BUFFER_SIZE


class MoodLogger:
    """
    Thread-safe CSV logger with write buffering.

    Improvement over v1:
      - Buffers LOG_BUFFER_SIZE entries in memory before writing.
      - Single file open per flush instead of per log entry.
      - Explicit flush() for graceful app shutdown.
    """

    def __init__(self):
        self._file: str = MOOD_LOG_FILE
        self._buffer: list = []
        self._lock = threading.Lock()

        if not os.path.exists(self._file):
            with open(self._file, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(["time", "emotion", "confidence"])

    # ── Public API ────────────────────────────────────────────────────────────

    def log(self, emotion: str, confidence: float) -> None:
        """Buffer a mood entry. Flushes automatically when buffer is full."""
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            emotion,
            f"{confidence:.1f}",
        ]
        with self._lock:
            self._buffer.append(row)
            if len(self._buffer) >= LOG_BUFFER_SIZE:
                self._flush_locked()

    def flush(self) -> None:
        """Force-write all buffered entries to disk (call on app close)."""
        with self._lock:
            self._flush_locked()

    def get_history(self) -> list:
        """Return the last HISTORY_DISPLAY mood entries."""
        self.flush()   # Ensure latest buffered entries are visible
        if not os.path.exists(self._file):
            return []
        with open(self._file, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        return rows[-HISTORY_DISPLAY:]

    # ── Internal ──────────────────────────────────────────────────────────────

    def _flush_locked(self) -> None:
        """Write all buffered rows to CSV. Must be called with self._lock held."""
        if not self._buffer:
            return
        with open(self._file, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows(self._buffer)
        self._buffer.clear()