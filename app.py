import streamlit as st
import random
import numpy as np
import cv2
from googleapiclient.discovery import build
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# === CONFIG - replace with your keys ===
YOUTUBE_API_KEY = "AIzaSyDDFUI6CbPWoTCuivwY2j_ONF6vMWbCb5U"          
SPOTIFY_CLIENT_ID = "032112ad1ef64e43be2e42ed8b869100"      
SPOTIFY_CLIENT_SECRET = "1926409223b04fca89ef293e5768a146"
# ========================================

st.set_page_config(page_title="Euphony", page_icon="🎧")
st.title("🎧 Euphony — Emotion Adaptive Music Player")

# Initialize YouTube
try:
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
except Exception as e:
    youtube = None
    st.error("YouTube API init failed. Check your API key.")

# Initialize Spotify
try:
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET
    ))
except Exception as e:
    sp = None
    st.error("Spotify init failed. Check your client ID/secret.")

# Mappings
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

# ---------- session handling ----------
if "emotion" not in st.session_state:
    st.session_state.emotion = None
if "activity" not in st.session_state:
    st.session_state.activity = None

# ---------- detection helpers ----------
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

def detect_emotion_from_face(img_bytes):
    try:
        from fer import FER
    except Exception:
        st.error("FER not available. pip install fer tensorflow-cpu")
        return None
    file_bytes = np.asarray(bytearray(img_bytes.read()), dtype=np.uint8)
    frame = cv2.imdecode(file_bytes, 1)
    if frame is None:
        return None
    detector = FER(mtcnn=True)
    em, score = detector.top_emotion(frame)
    if em:
        return em.lower()
    return None

# ---------- music fetchers ----------
def youtube_search(emotion, language=None, max_results=6):
    if youtube is None:
        return []
    queries = EMOTION_QUERIES.get(emotion, ["music"])
    q = random.choice(queries)
    if language:
        q = f"{q} {language} songs"
    req = youtube.search().list(part="snippet", q=q, type="video", maxResults=max_results)
    res = req.execute()
    videos = []
    for item in res.get("items", []):
        vid = item["id"]["videoId"]
        title = item["snippet"]["title"]
        videos.append({"title": title, "url": f"https://www.youtube.com/watch?v={vid}"})
    return videos

def spotify_search(emotion, language=None, limit=8):
    if sp is None:
        return []
    qmap = {
        "happy":"happy upbeat",
        "sad":"sad acoustic",
        "angry":"energetic rock",
        "calm":"calm instrumental",
        "energetic":"workout",
        "neutral":"chill"
    }
    q = qmap.get(emotion, "music")
    if language:
        q += f" {language}"  # add language to query
    res = sp.search(q=q, type="track", limit=limit)
    tracks = []
    for t in res.get('tracks', {}).get('items', []):
        tracks.append({
            "name": t['name'],
            "artist": t['artists'][0]['name'],
            "spotify_url": t['external_urls']['spotify'],
            "preview_url": t.get('preview_url')
        })
    return tracks

# ---------- UI ----------
mode = st.radio("Choose input mode:", ["Face", "Text", "Emoji", "Activity"])

# ---------- Mode Handling ----------
if mode == "Face":
    img = st.camera_input("Take a picture")
    if img:
        with st.spinner("Detecting..."):
            st.session_state.emotion = detect_emotion_from_face(img)
        if st.session_state.emotion:
            st.success(f"Face emotion: {st.session_state.emotion}")
        else:
            st.warning("Could not detect face emotion. Try Text/Emoji mode.")

elif mode == "Text":
    txt = st.text_input("Type how you feel (example: I am tired or I am happy):")
    if st.button("Detect Text Emotion"):
        st.session_state.emotion = detect_emotion_from_text(txt)
        st.success(f"Text emotion: {st.session_state.emotion}")

elif mode == "Emoji":
    em = st.text_input("Paste an emoji (e.g. 😊):")
    if st.button("Detect Emoji Emotion"):
        st.session_state.emotion = detect_emotion_from_emoji(em)
        st.success(f"Emoji emotion: {st.session_state.emotion}")

else:  # Activity
    act = st.selectbox("Select activity:", list(ACTIVITY_TO_EMOTION.keys()))
    if st.button("Use Activity"):
        st.session_state.activity = act
        st.session_state.emotion = ACTIVITY_TO_EMOTION.get(act)
        st.success(f"Activity mapped to emotion: {st.session_state.emotion}")

# ---------- Music Display ----------
emotion_to_use = st.session_state.emotion
if emotion_to_use:
    st.markdown("---")
    st.subheader(f"Music for *{emotion_to_use}* mood")

    source = st.radio("Choose source:", ["YouTube", "Spotify"], key="source_radio")
    lang = st.selectbox("Prefer language (optional):", ["Any","Hindi","English","Telugu","Tamil","Kannada","Malayalam","Spanish"], key="lang_select")
    lang_query = None if lang=="Any" else lang

    if source == "Spotify":
        tracks = spotify_search(emotion_to_use, language=lang_query, limit=8)
        if not tracks:
            st.info("No Spotify tracks found — falling back to YouTube.")
            source = "YouTube"  # fallback
        else:
            for t in tracks:
                st.markdown(f"{t['name']} — {t['artist']} → [Open in Spotify]({t['spotify_url']})")
                if t.get('preview_url'):
                    st.audio(t['preview_url'])

    if source == "YouTube":
        videos = youtube_search(emotion_to_use, language=lang_query, max_results=6)
        for v in videos:
            st.markdown(f"{v['title']}")
            st.video(v['url'])
