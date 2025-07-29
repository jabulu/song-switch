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

