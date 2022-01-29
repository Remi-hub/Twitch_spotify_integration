import json
import requests
from dotenv import load_dotenv
import os
import playsound

load_dotenv()

SPOTIFY_CODE = os.getenv("SPOTIFY_CODE")
BASIC64_AUTHORIZATION = os.getenv("BASIC64_AUTHORIZATION")
REDIRECT_URI = os.getenv("REDIRECT_URI")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")


def access_token_and_refresh_token():
    url = "https://accounts.spotify.com/api/token"
    payload = (
        f"grant_type=authorization_code&code="
        f"{SPOTIFY_CODE}&redirect_uri={REDIRECT_URI}"
    )
    headers = {
        # Base 64 encoded string that contains the client ID and client secret key of spotify app.
        # The field must have the format:
        # Authorization: Basic <base64 encoded client_id:client_secret>
        "Authorization": f"{BASIC64_AUTHORIZATION}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    response = response.json()

    access_token = response["access_token"]
    refresh_token = response["refresh_token"]

    return access_token, refresh_token


def refreshed_token():
    url = "https://accounts.spotify.com/api/token"

    payload = f"grant_type=refresh_token&refresh_token={REFRESH_TOKEN}&client_id={SPOTIFY_CLIENT_ID}"
    headers = {
        "Authorization": f"{BASIC64_AUTHORIZATION}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    response = response.json()
    access_token = response["access_token"]
    return access_token


def get_track_uri(name, access_token):
    """take the name of a song and return its uri"""
    url = f"https://api.spotify.com/v1/search?q={name}&type=track"

    payload = {}
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.request("GET", url, headers=headers, data=payload)
    response_json = response.json()
    song_found = response_json["tracks"]["items"]
    if not song_found:
        print("***   No Song found   ***")
    else:
        song_name = response_json["tracks"]["items"][0]["name"]
        song_id = response_json["tracks"]["items"][0]["id"]
        song_uri = response_json["tracks"]["items"][0]["uri"]
        return song_uri


def skip_current_track():
    url = "https://api.spotify.com/v1/me/player/next"

    payload = {}
    headers = {
        "Authorization": f"Bearer {refreshed_token()}",
        "Content-Type": "application/json",
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    playsound.playsound("./media/dj-scratch.mp3")


def add_track_to_playback(song_uri):
    url = f"https://api.spotify.com/v1/me/player/queue?uri={song_uri}"

    payload = {}
    headers = {"Authorization": f"Bearer {refreshed_token()}"}

    response = requests.request("POST", url, headers=headers, data=payload)


def play_music_requested(user_input):
    add_track_to_playback(
        get_track_uri(user_input, refreshed_token()),
    )
