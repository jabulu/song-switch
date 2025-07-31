# main Flask app
from youtube_routes import youtube_bp
from spotify_routes import spotify_bp
from flask import Flask, redirect, session, request, url_for
from auth import create_spotify_oauth
import spotipy 
from spotipy.exceptions import SpotifyException
import re 
import os
from dotenv import load_dotenv
from flask_session import Session

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")


app.register_blueprint(youtube_bp)
app.register_blueprint(spotify_bp)

@app.route('/')
def index():
    return '<a href="/login">Login with Spotify</a>'




# routes
# @app.route('/get_playlists')
# def get_playlists():
#     sp_oauth = create_spotify_oauth()
#     token_info = session.get('token_info', None)
#     if not token_info:
#         return redirect('/')
#     if sp_oauth.is_token_expired(token_info):
#         token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
#         session['token_info'] = token_info
#     sp = spotipy.Spotify(auth=token_info['access_token'])
#     playlists = sp.current_user_playlists()
#     if not playlists or 'items' not in playlists:
#         return 'No playlists found or invalid response from Spotify.'
#     links = []
#     for p in playlists['items']:
#         link = url_for('view_playlist', playlist_id=p['id'])
#         links.append(f'<a href="{link}">{p["name"]}</a>')

#     return '<br>'.join(links)

# @app.route('/playlist/<playlist_id>')
# def view_playlist(playlist_id):
#     sp_oauth = create_spotify_oauth()
#     token_info = session.get('token_info')
#     if not token_info:
#         return redirect('/login')
#     if sp_oauth.is_token_expired(token_info):
#         token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
#         session['token_info'] = token_info
#     sp = spotipy.Spotify(auth=token_info['access_token'])
#     tracks = sp.playlist_tracks(playlist_id)
#     if not tracks or 'items' not in tracks:
#         return 'No tracks found or invalid response from Spotify.'
#     return '<br>'.join([t['track']['name'] for t in tracks['items']])

# @app.route('/copy_playlist')
# def copy_playlist():
#     token_info = session.get('token_info')
#     if not token_info:
#         return redirect('/login')

#     sp_oauth = create_spotify_oauth()
#     if sp_oauth.is_token_expired(token_info):
#         token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
#         session['token_info'] = token_info

#     sp = spotipy.Spotify(auth=token_info['access_token'])

#     user = sp.me()
#     if not user:
#         return 'Not logged in'
#     user_id = user['id']

#     # Accept full URL or raw ID
#     source_input = request.args.get('source_id')
#     if not source_input:
#         return 'Missing source playlist ID.'

#     match = re.search(r'playlist/([a-zA-Z0-9]+)', source_input)
#     if match:
#         source_playlist_id = match.group(1)
#     else:
#         print("No match found, using raw input as playlist ID.")
#         source_playlist_id = source_input  # assume it's already just the ID
#     new_name = request.args.get('name', 'Copied Playlist')

#     try:
#         tracks = sp.playlist_tracks(source_playlist_id)
#     except SpotifyException:
#         return 'Could not fetch tracks from playlist. Make sure the playlist is public and valid.'

#     if not tracks or 'items' not in tracks:
#         return 'No tracks found or invalid response from Spotify.'

#     track_ids = [t['track']['id'] for t in tracks['items'] if t['track'] and t['track']['id']]

#     new_playlist = sp.user_playlist_create(user=user_id, name=new_name, public=False)
#     if not new_playlist or 'id' not in new_playlist:
#         return 'Failed to create new playlist.'

#     new_playlist_id = new_playlist['id']
#     sp.user_playlist_add_tracks(user=user_id, playlist_id=new_playlist_id, tracks=track_ids)

#     playlist_url = new_playlist['external_urls']['spotify']
#     return f'{len(track_ids)} songs copied to new playlist: <a href="{playlist_url}">{new_name}</a>'





# things to add:
# - pagination support for large playlists
# - rate limit handling
# - error pages
# - logging

# test:
# 0 track playlists, invalid/private playlist URLs, running route twice

if __name__ == '__main__':
    app.run(port=8080)