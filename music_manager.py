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
from config import MOOD_SONGS, SONG_COOLDOWN_SECONDS, EMOTION_COOLDOWNS, MOOD_SHIFT_BYPASS_THRESHOLD

# Priority scale used to detect "major mood shifts"
# Emotions far apart in priority can bypass the cooldown immediately.
_EMOTION_PRIORITY: dict = {
    "angry":    0,
    "fear":     1,
    "sad":      2,
    "disgust":  3,
    "surprise": 4,
    "neutral":  5,
    "happy":    6,
}


class MusicManager:
    """
    Plays music based on detected emotion.

    Improvements over v1:
      - Per-emotion cooldowns (angry: 90s, neutral: 180s, etc.)
      - Major mood-shift bypass: if the new emotion is emotionally distant
        from the current one, the cooldown is skipped entirely.
      - Global recently-played deque prevents exact URL repeats across emotions.
    """

    def __init__(self):
        # Per-emotion last-played timestamps
        self._last_song_times: dict = {}
        self._lock = threading.Lock()
        self._played_recently: dict = {}
        self.current_mood: str | None = None
        self.current_url: str | None = None

    # ── Public API ────────────────────────────────────────────────────────────

    def try_play(self, emotion: str) -> tuple[bool, str]:
        with self._lock:
            now = time.time()
            cooldown = EMOTION_COOLDOWNS.get(emotion, SONG_COOLDOWN_SECONDS)
            last = self._last_song_times.get(emotion, 0)
            elapsed = now - last
            remaining = cooldown - elapsed

            in_cooldown = elapsed < cooldown
            major_shift = self._is_major_shift(emotion)

            if in_cooldown and not major_shift:
                return False, f"Cooldown: {int(remaining)}s left"

            # Pick a song not played recently
            links = MOOD_SONGS.get(emotion, MOOD_SONGS["neutral"])
            if emotion not in self._played_recently:
                self._played_recently[emotion] = deque(maxlen=max(1, len(links) - 1))
            
            history = self._played_recently[emotion]
            fresh = [l for l in links if l not in history]
            if not fresh:
                fresh = list(links)
                history.clear()

            chosen = random.choice(fresh)
            history.append(chosen)
            self._last_song_times[emotion] = now
            self.current_mood = emotion
            self.current_url = chosen

        # Open browser outside the lock to avoid blocking
        webbrowser.open(chosen)
        return True, f"Opened YouTube for '{emotion}'"

    def time_until_next(self) -> int:
        """Returns seconds until the current mood's cooldown expires."""
        with self._lock:
            if self.current_mood is None:
                return 0
            cooldown = EMOTION_COOLDOWNS.get(self.current_mood, SONG_COOLDOWN_SECONDS)
            last = self._last_song_times.get(self.current_mood, 0)
            elapsed = time.time() - last
            return max(0, int(cooldown - elapsed))

    # ── Internal ──────────────────────────────────────────────────────────────

    def _is_major_shift(self, new_emotion: str) -> bool:
        """
        Returns True if the new emotion is emotionally distant enough from
        the current one to justify bypassing the cooldown.
        E.g. neutral (5) → angry (0) = distance 5 ≥ threshold 3 → bypass.
        """
        if self.current_mood is None:
            return True
        old_pri = _EMOTION_PRIORITY.get(self.current_mood, 5)
        new_pri = _EMOTION_PRIORITY.get(new_emotion, 5)
        return abs(old_pri - new_pri) >= MOOD_SHIFT_BYPASS_THRESHOLD