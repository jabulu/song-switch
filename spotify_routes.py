# spotify_routes.py
from flask import Blueprint, request
from spotify_client import get_user_playlists, get_playlist_tracks, copy_playlist
from flask import Flask, redirect, session, request, url_for
from auth import create_spotify_oauth

spotify_bp = Blueprint("spotify", __name__)

@spotify_bp.route('/login')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@spotify_bp.route('/callback')
def callback():
    session.clear()
    sp_oauth = create_spotify_oauth()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    print(token_info)
    return redirect(url_for('spotify.get_playlists_route', _external=True))


@spotify_bp.route('/get_playlists')
def get_playlists_route():
    result = get_user_playlists()
    if isinstance(result, list):
        links = [f'<a href="/playlist/{p["id"]}">{p["name"]}</a>' for p in result]
        return '<br>'.join(links)
    return result

@spotify_bp.route('/playlist/<playlist_id>')
def view_playlist_route(playlist_id):
    result = get_playlist_tracks(playlist_id)
    if isinstance(result, list):
        return '<br>'.join(result)
    return result

@spotify_bp.route('/copy_playlist')
def copy_playlist_route():
    source_input = request.args.get('source_id')
    new_name = request.args.get('name', 'Copied Playlist')
    return copy_playlist(source_input, new_name)

@spotify_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')