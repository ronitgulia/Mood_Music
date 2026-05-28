# ─────────────────────────────────────────────
# Mood Music Player
# Author: Ronit Gulia
# GitHub: https://github.com/ronitgulia
# Date: April 2026
# Description: Opens YouTube songs based on detected emotion
# ─────────────────────────────────────────────

import webbrowser
import threading
import time
import random
from collections import deque
from config import MOOD_SONGS, SONG_COOLDOWN_SECONDS

class MusicManager:
    def __init__(self):
        self._last_song_time = 0
        self._lock = threading.Lock()
        self._played_recently = deque(maxlen=10)
        self.current_mood = None
        self.current_url = None

    def try_play(self, emotion):
        with self._lock:
            elapsed = time.time() - self._last_song_time
            remaining = SONG_COOLDOWN_SECONDS - elapsed

            if elapsed < SONG_COOLDOWN_SECONDS:
                return False, f"Cooldown: {int(remaining)}s left"

            links = MOOD_SONGS.get(emotion, MOOD_SONGS["neutral"])

            fresh = [l for l in links if l not in self._played_recently]
            if not fresh:
                fresh = links
                self._played_recently.clear()

            chosen = random.choice(fresh)
            self._played_recently.append(chosen)
            self._last_song_time = time.time()
            self.current_mood = emotion
            self.current_url = chosen

            webbrowser.open(chosen)
            return True, f"Opened YouTube for '{emotion}'"

    def time_until_next(self):
        with self._lock:
            elapsed = time.time() - self._last_song_time
            return max(0, int(SONG_COOLDOWN_SECONDS - elapsed))