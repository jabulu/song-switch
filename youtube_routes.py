# youtube_routes.py
from flask import Blueprint, redirect, session, request, url_for
from youtube_client import get_youtube_auth_url, copy_spotify_to_youtube
from google_auth_oauthlib.flow import Flow
from youtube_client import copy_spotify_to_youtube
from youtube_client import CLIENT_SECRETS_FILE, SCOPES
from flask import current_app


youtube_bp = Blueprint("youtube", __name__)

@youtube_bp.route("/youtube_auth")
def youtube_auth():
    return redirect(url_for("youtube.start_youtube_oauth"))

@youtube_bp.route("/youtube_start")
def start_youtube_oauth():
    return redirect(get_youtube_auth_url())


    return redirect(auth_url)

@youtube_bp.route("/youtube_callback")
def youtube_callback():
    stored_state = session.get("state")
    received_state = request.args.get("state")
    print("Session state stored before redirect:", stored_state)
    print("State received back from Google:", received_state)

    if not stored_state or stored_state != received_state:
        return "Invalid or missing OAuth session state."

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=stored_state,
        redirect_uri="http://127.0.0.1:8080/youtube_callback"
    )

    try:
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials

        session["youtube_credentials"] = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes,
        }

        return "YouTube authentication successful!"
    except Exception as e:
        return f"Auth failed: {e}"




@youtube_bp.route("/youtube_copy")
def youtube_copy():
    source_id = request.args.get("source_id")
    new_name = request.args.get("name", "Imported from Spotify")
    
    result, redirect_resp = copy_spotify_to_youtube(source_id, new_name)
    
    if redirect_resp:
        return redirect_resp
    return result

