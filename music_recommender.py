# music_recommender.py
import random
from googleapiclient.discovery import build
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from emotion_mapping import EMOTION_QUERIES

# --- Configure your API keys ---
YOUTUBE_API_KEY = "AIzaSyDDFUI6CbPWoTCuivwY2j_ONF6vMWbCb5U"          
SPOTIFY_CLIENT_ID = "032112ad1ef64e43be2e42ed8b869100"      
SPOTIFY_CLIENT_SECRET = "1926409223b04fca89ef293e5768a146"

# --- Initialize APIs ---
youtube = None
sp = None
try:
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
except Exception:
    youtube = None

try:
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    ))
except Exception:
    sp = None

# --- YouTube search ---
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

# --- Spotify search ---
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
        q = f"{q} {language}"
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
