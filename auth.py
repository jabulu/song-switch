from dotenv import load_dotenv
import os
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope="playlist-read-private playlist-modify-private playlist-modify-public"
    )
