# ─────────────────────────────────────────────
# Mood Music Player
# Author: Ronit Gulia
# GitHub: https://github.com/ronitgulia
# Date: April 2026
# Description: All settings and song configurations
# ─────────────────────────────────────────────

CONFIDENCE_THRESHOLD = 30
CONFIRM_COUNT_NEEDED = 2
SONG_COOLDOWN_SECONDS = 180
ANALYSIS_INTERVAL = 0.8
MOOD_LOG_FILE = "mood_log.csv"
VOICE_ENABLED = True
HISTORY_DISPLAY = 15

EMOTION_COLORS = {
    "happy":   "#FFD700",
    "sad":     "#4A90D9",
    "angry":   "#FF4444",
    "neutral": "#888888",
    "surprise":"#FF69B4",
    "fear":    "#9B59B6",
    "disgust": "#27AE60",
}

MOOD_SONGS = {
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