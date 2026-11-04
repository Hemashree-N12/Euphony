# emotion_mapping.py

ACTIVITY_TO_EMOTION = {
    "Studying": "calm",
    "Working Out": "energetic",
    "Cleaning": "happy",
    "Relaxing": "calm",
    "Cooking": "happy",
    "Traveling": "energetic",
    "Meditation": "calm"
}

EMOTION_QUERIES = {
    "happy": ["happy songs", "upbeat songs", "feel good music"],
    "sad": ["sad songs", "emotional acoustic"],
    "angry": ["rock music", "intense tracks"],
    "calm": ["lofi study music", "relaxing instrumental"],
    "energetic": ["workout music", "dance hits"],
    "neutral": ["chill music", "lofi beats"]
}

def detect_emotion_from_text(text: str):
    if not text:
        return None
    t = text.lower()
    if any(w in t for w in ["happy","great","good","joy","awesome","smile"]):
        return "happy"
    if any(w in t for w in ["sad","down","unhappy","depressed","cry"]):
        return "sad"
    if any(w in t for w in ["angry","mad","furious","hate"]):
        return "angry"
    if any(w in t for w in ["tired","sleep","bored","relax"]):
        return "calm"
    if any(w in t for w in ["excited","pumped","energetic"]):
        return "energetic"
    return "neutral"

def detect_emotion_from_emoji(e: str):
    if not e:
        return None
    if any(ch in e for ch in ["😊","😀","😄","😁","🙂"]):
        return "happy"
    if any(ch in e for ch in ["😢","😭","☹","😞"]):
        return "sad"
    if any(ch in e for ch in ["😡","🤬","😤"]):
        return "angry"
    return "neutral"
