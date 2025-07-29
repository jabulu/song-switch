# youtube_app.py
from flask import Blueprint, redirect, request, session
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
import google.oauth2.credentials

load_dotenv()

youtube_bp = Blueprint("youtube", __name__)
CLIENT_SECRETS_FILE = os.getenv("GOOGLE_CLIENT_SECRET_PATH", "client_secret.json")
SCOPES = ["https://www.googleapis.com/auth/youtube"]
REDIRECT_URI = "http://localhost:5000/youtube_callback"

@youtube_bp.route("/youtube_auth")
def youtube_auth():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    auth_url, state = flow.authorization_url(prompt='consent')
    session["state"] = state
    return redirect(auth_url)

@youtube_bp.route("/youtube_callback")
def youtube_callback():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    session["youtube_credentials"] = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        # "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes
    }
    return "YouTube authentication successful!"

