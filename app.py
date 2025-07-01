# main Flask app
from flask import Flask, redirect, session, request, url_for
from auth import create_spotify_oauth

app = Flask(__name__)

@app.route('/')
def index():
    return '<a href="/login">Login with Spotify</a>'

@app.route('/login')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback(code):
    session.clear()
    sp_oauth = create_spotify_oauth()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect(url_for('get_playlists', _external=True))




if __name__ == '__main__':
    app.run(port=8080)