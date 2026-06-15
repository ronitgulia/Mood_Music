# ─────────────────────────────────────────────
# Mood Music Player
# Author: Ronit Gulia
# GitHub: https://github.com/ronitgulia
# Date: April 2026
# Description: All settings and song configurations
# ─────────────────────────────────────────────

# ── Detection thresholds ──────────────────────────────────────────────────────
CONFIDENCE_THRESHOLD: int = 40        # Min smoothed confidence (%) to accept a result
ANALYSIS_INTERVAL: float = 0.35       # Seconds between analysis frames (was 0.5)

# ── Temporal smoothing (EMA) ──────────────────────────────────────────────────
SMOOTHING_ALPHA: float = 0.35         # EMA weight: higher = more reactive, lower = smoother

# ── Voting-window confirmation ────────────────────────────────────────────────
VOTE_WINDOW: int = 8                  # Number of recent predictions to vote over
VOTE_THRESHOLD: float = 0.60         # Fraction of votes needed to confirm an emotion

# ── Logging & history ─────────────────────────────────────────────────────────
MOOD_LOG_FILE: str = "mood_log.csv"
HISTORY_DISPLAY: int = 15
LOG_BUFFER_SIZE: int = 5             # Write to CSV after this many buffered entries

# ── Voice ─────────────────────────────────────────────────────────────────────
VOICE_ENABLED: bool = True

# ── Per-emotion song cooldowns (seconds) ─────────────────────────────────────
# Different emotions get different cooldowns — angry/fear/surprise can
# switch sooner; neutral waits longer.
EMOTION_COOLDOWNS: dict = {
    "happy":    120,
    "sad":      150,
    "angry":     90,
    "neutral":  180,
    "surprise":  60,
    "fear":     120,
    "disgust":  120,
}
SONG_COOLDOWN_SECONDS: int = 120     # Fallback if emotion not in EMOTION_COOLDOWNS

# ── Mood shift bypass ─────────────────────────────────────────────────────────
# If the new emotion is >= this many priority levels away from the current one,
# skip the cooldown and play immediately (e.g. neutral → angry).
MOOD_SHIFT_BYPASS_THRESHOLD: int = 3

# ── Emotion colours (used by GUI) ─────────────────────────────────────────────
EMOTION_COLORS: dict = {
    "happy":    "#FFD700",
    "sad":      "#4A90D9",
    "angry":    "#FF4444",
    "neutral":  "#888888",
    "surprise": "#FF69B4",
    "fear":     "#9B59B6",
    "disgust":  "#27AE60",
}

# ── Song library ──────────────────────────────────────────────────────────────
MOOD_SONGS: dict = {
    "happy": [
        "https://www.youtube.com/watch?v=2edFgRpgisk&list=RD2edFgRpgisk&start_radio=1",   # Good Luck Charm - Aman Hayer
        "https://www.youtube.com/watch?v=Dl_n2_ekfN4&list=RDDl_n2_ekfN4&start_radio=1",   # Midnight Call - Harkirat Sangha
        "https://www.youtube.com/watch?v=xciwYxZuxog&list=RDxciwYxZuxog&start_radio=1",   # You're U Tho - Karan Aujla
    ],
    "sad": [
        "https://www.youtube.com/watch?v=61floBUAiTY&list=RD61floBUAiTY&start_radio=1",   # Tu Hai Ki Nahi - Ankit Tiwari
        "https://www.youtube.com/watch?v=-FP2Cmc7zj4&list=RD-FP2Cmc7zj4&start_radio=1",   # Labon Ko - Pritam
        "https://www.youtube.com/watch?v=snb-h8zKE6M&list=RDsnb-h8zKE6M&start_radio=1",   # Taara - Ammy Virk
    ],
    "angry": [
        "https://www.youtube.com/watch?v=Xc1sdGMF9rc&list=RDXc1sdGMF9rc&start_radio=1",   # 10 Mint - Sippy Gill
        "https://www.youtube.com/watch?v=F02gxrMcvCY&list=RDF02gxrMcvCY&start_radio=1",   # Vailpuna - Sippy Gill
        "https://www.youtube.com/watch?v=L0i7AkGtbu8&list=RDL0i7AkGtbu8&start_radio=1",   # Don't Mess 1.0 - Yudhvir Shergill
    ],
    "neutral": [
        "https://www.youtube.com/watch?v=Llav5_-5idA&list=RDLlav5_-5idA&start_radio=1",   # Ghane Gande - Sumit Parta
        "https://www.youtube.com/watch?v=fD8tlTZfhN0&list=RDfD8tlTZfhN0&start_radio=1",   # Laarey - Hay Bee
        "https://www.youtube.com/watch?v=ZZHIF_lYOf8&list=RDZZHIF_lYOf8&start_radio=1",   # Kala Asla - MC Square
    ],
    "surprise": [
        "https://www.youtube.com/watch?v=Umqb9KENgmk&list=RDUmqb9KENgmk&start_radio=1",   # Tum Hi Ho - Arijit Singh
        "https://www.youtube.com/watch?v=v0yIfGsGB24&list=RDv0yIfGsGB24&start_radio=1",   # Law - Preet Harpal
        "https://www.youtube.com/watch?v=BtQp2U6hJII&list=RDBtQp2U6hJII&start_radio=1",   # White Brown Black - Karan Aujla
    ],
    "fear": [
        "https://www.youtube.com/watch?v=jTNu-R9KA-4&list=RDjTNu-R9KA-4&start_radio=1",   # Hanuman Chalisa - Shankar Mahadevan
        "https://www.youtube.com/watch?v=mUbi7EK6fu4&list=RDmUbi7EK6fu4&start_radio=1",   # Sankat Mochan - Rasraj Ji Maharaj
        "https://www.youtube.com/watch?v=wuYgr4gcNLw&list=RDwuYgr4gcNLw&start_radio=1",   # Bajrang Baan - Rasraj Ji Maharaj
    ],
    "disgust": [
        "https://www.youtube.com/watch?v=m1rcse8INWk&list=RDm1rcse8INWk&start_radio=1",   # Phir Mohabbat - Mohammed Irfan
        "https://www.youtube.com/watch?v=-6wqeLojrOA&list=RD-6wqeLojrOA&start_radio=1",   # Chhad Dila - Lehmber Hussainpuri
        "https://www.youtube.com/watch?v=moIXcDQB9-g&list=RDmoIXcDQB9-g&start_radio=1",   # Koi Si - Afsana Khan
    ],
}