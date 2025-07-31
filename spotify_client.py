import re
import spotipy
from flask import session, redirect
from spotipy.exceptions import SpotifyException
from auth import create_spotify_oauth



def get_valid_spotify_client():
    sp_oauth = create_spotify_oauth()
    token_info = session.get('token_info')

    if not token_info:
        return None, redirect('/login')

    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session['token_info'] = token_info

    sp = spotipy.Spotify(auth=token_info['access_token'])
    return sp, None

def get_user_playlists():
    sp, redirect_response = get_valid_spotify_client()
    if redirect_response or sp is None:
        return redirect_response or redirect('/login')

    try:
        playlists = sp.current_user_playlists()
        if playlists and isinstance(playlists, dict) and 'items' in playlists:
            return playlists['items']
        return []
    except Exception:
        return 'Failed to fetch playlists.'

def get_playlist_tracks(playlist_id):
    sp, redirect_response = get_valid_spotify_client()
    if redirect_response or sp is None:
        return redirect_response or redirect('/login')

    try:
        tracks = sp.playlist_tracks(playlist_id)
        if not tracks or 'items' not in tracks:
            return 'No tracks found or invalid response from Spotify.'
        return [t['track']['name'] for t in tracks['items'] if t.get('track')]
    except SpotifyException:
        return 'No tracks found or invalid response from Spotify.'

def copy_playlist(source_input, new_name='Copied Playlist'):
    sp, redirect_response = get_valid_spotify_client()
    if redirect_response or sp is None:
        return redirect_response or redirect('/login')

    try:
        user = sp.me()
        user_id = user['id'] if user and 'id' in user else None
        if not user_id:
            return 'User ID not found.'
    except Exception:
        return 'Not logged in'

    # Accept raw ID or full URL
    match = re.search(r'playlist/([a-zA-Z0-9]+)', source_input)
    source_playlist_id = match.group(1) if match else source_input

    try:
        tracks = sp.playlist_tracks(source_playlist_id)
        if not tracks or 'items' not in tracks:
            return 'No tracks found or invalid playlist.'
        track_items = tracks['items']
    except SpotifyException:
        return 'Could not fetch tracks from playlist. Make sure it is public and valid.'

    track_ids = [
        t['track']['id']
        for t in track_items
        if t.get('track') and t['track'].get('id')
    ]

    try:
        new_playlist = sp.user_playlist_create(user=user_id, name=new_name, public=False)
        if not new_playlist or 'id' not in new_playlist:
            return 'Failed to create new playlist.'

        new_playlist_id = new_playlist['id']
        sp.user_playlist_add_tracks(user=user_id, playlist_id=new_playlist_id, tracks=track_ids)

        playlist_url = new_playlist.get('external_urls', {}).get('spotify', '#')
        return f'{len(track_ids)} songs copied to new playlist: <a href="{playlist_url}">{new_name}</a>'
    except Exception:
        return 'Failed to create or populate new playlist.'

def get_youtube_playlist_tracks(youtube, playlist_id):
    tracks = []
    request = youtube.playlistItems().list(
        part="snippet",
        maxResults=50,
        playlistId=playlist_id
    )

    while request:
        response = request.execute()
        for item in response["items"]:
            title = item["snippet"]["title"]
            channel = item["snippet"].get("videoOwnerChannelTitle", "")
            tracks.append({"title": title, "channel": channel})
        request = youtube.playlistItems().list_next(request, response)

    return tracks

def parse_youtube_title(title):
    # Remove any parenthetical content
    title = re.sub(r"\([^)]*\)", "", title)
    title = re.sub(r"\[[^\]]*\]", "", title)
    title = title.replace("official video", "")
    title = title.replace("official audio", "")
    title = title.replace("HQ", "")
    title = title.replace("HD", "")
    title = title.strip()

    if "-" in title:
        artist, track = title.split("-", 1)
        return artist.strip(), track.strip()

    return "", title.strip()

def search_spotify_track(sp, artist, track):
    query = f"{track} {artist}".strip()
    result = sp.search(q=query, type="track", limit=1)
    items = result.get("tracks", {}).get("items", [])
    if items:
        return items[0]["uri"]
    return None

def copy_youtube_to_spotify(yt_playlist_id, new_name="Imported from YouTube"):
    from youtube_client import get_authenticated_youtube_client
    sp, redirect_response = get_valid_spotify_client()
    if redirect_response or sp is None:
        return redirect_response or redirect('/login')
    youtube, redirect_resp = get_authenticated_youtube_client()
    if redirect_resp:
        return None, redirect_resp

    # Get YouTube tracks
    yt_tracks = get_youtube_playlist_tracks(youtube, yt_playlist_id)
    if not yt_tracks:
        return "Failed to fetch YouTube playlist.", None

    # Search Spotify
    uris = []
    for yt_track in yt_tracks:
        artist, track = parse_youtube_title(yt_track["title"])
        print("YouTube Title:", yt_track["title"])
        print("Parsed as:", f"{artist} - {track}")
        if not track:
            print("Skipping: no track name parsed.\n")
            continue
        uri = search_spotify_track(sp, artist, track)
        if uri:
            print("Match found:", uri)
            uris.append(uri)

    if not uris:
        return "No matching Spotify tracks found.", None

    # Create Spotify playlist & add tracks
    user_id = sp.me()["id"]
    playlist = sp.user_playlist_create(user=user_id, name=new_name, public=False)
    sp.playlist_add_items(playlist_id=playlist["id"], items=uris)

    return f"{len(uris)} tracks added to Spotify.", None
