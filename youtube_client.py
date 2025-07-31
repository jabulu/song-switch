# youtube_client.py
import os
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from flask import request, session, redirect
from dotenv import load_dotenv
from spotify_client import get_playlist_tracks
from google.oauth2.credentials import Credentials


load_dotenv()
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

CLIENT_SECRETS_FILE = os.getenv("GOOGLE_CLIENT_SECRET_PATH", "client_secret.json")
SCOPES = ["https://www.googleapis.com/auth/youtube"]

def get_youtube_auth_url():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri="http://127.0.0.1:8080/youtube_callback"
    )
    auth_url, state = flow.authorization_url(prompt="consent")
    session["state"] = state
    return auth_url

def get_authenticated_youtube_client():
    creds_data = session.get("youtube_credentials")
    if not creds_data:
        return None, redirect("/youtube_auth")

    credentials = Credentials(**creds_data)
    youtube = build("youtube", "v3", credentials=credentials)
    return youtube, None

def get_user_playlists():
    youtube, redirect_resp = get_authenticated_youtube_client()
    if redirect_resp:
        return redirect_resp

    playlists = []
    request = youtube.playlists().list(part="snippet", mine=True, maxResults=50)
    while request:
        response = request.execute()
        playlists.extend(response.get("items", []))
        request = youtube.playlists().list_next(request, response)

    return playlists

def get_playlist_video_titles(playlist_id):
    youtube, redirect_resp = get_authenticated_youtube_client()
    if redirect_resp:
        return redirect_resp

    titles = []
    request = youtube.playlistItems().list(part="snippet", playlistId=playlist_id, maxResults=50)
    while request:
        response = request.execute()
        for item in response.get("items", []):
            titles.append(item["snippet"]["title"])
        request = youtube.playlistItems().list_next(request, response)

    return titles

def create_youtube_playlist(name, description="Imported from Spotify"):
    youtube, redirect_resp = get_authenticated_youtube_client()
    if redirect_resp:
        return redirect_resp

    playlist = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {"title": name, "description": description},
            "status": {"privacyStatus": "private"}
        }
    ).execute()

    return playlist.get("id")

def search_and_add_video(youtube, playlist_id, track_name):
    search = youtube.search().list(
        part="snippet", q=track_name, maxResults=1, type="video"
    ).execute()

    if search["items"]:
        video_id = search["items"][0]["id"]["videoId"]
        youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }
        ).execute()
        return True
    return False


def copy_spotify_to_youtube(spotify_playlist_id, new_name="Imported from Spotify"):
    youtube, redirect_resp = get_authenticated_youtube_client()
    if redirect_resp:
        return None, redirect_resp

    # Get track names from Spotify
    tracks = get_playlist_tracks(spotify_playlist_id)
    if not isinstance(tracks, list) or not tracks:
        return "Failed to get tracks from Spotify.", None

    # Create YouTube playlist
    yt_playlist_id = create_youtube_playlist(new_name)
    if not yt_playlist_id:
        return "Failed to create YouTube playlist.", None

    # Add tracks
    added = 0
    for track in tracks:
        success = search_and_add_video(youtube, yt_playlist_id, track)
        if success:
            added += 1

    return f"{added} tracks added to YouTube playlist.", None
