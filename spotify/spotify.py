import json
import requests
from dotenv import load_dotenv
import os
import playsound
from bottle import route, run, static_file, request
from datetime import datetime
from threading import Thread

load_dotenv()

SPOTIFY_CODE = os.getenv("SPOTIFY_CODE")
BASIC64_AUTHORIZATION = os.getenv("BASIC64_AUTHORIZATION")
REDIRECT_URI = os.getenv("REDIRECT_URI")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
ACCESS_TOKEN = None
LAST_TIME_REFRESH = None


def refreshed_token(is_init=True):
    global ACCESS_TOKEN
    global LAST_TIME_REFRESH

    if is_init:
        LAST_TIME_REFRESH = datetime.now()
        url = "https://accounts.spotify.com/api/token"

        payload = f'grant_type=refresh_token&refresh_token={REFRESH_TOKEN}&client_id={SPOTIFY_CLIENT_ID}'
        headers = {
            'Authorization': f'{BASIC64_AUTHORIZATION}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        ACCESS_TOKEN = response["access_token"]
        return ACCESS_TOKEN
    else:
        actual_time = datetime.now()
        if (LAST_TIME_REFRESH - actual_time).seconds > 3500:
            new_token = refreshed_token(True)
            return new_token
        else:
            return ACCESS_TOKEN


refreshed_token(True)


def get_track_uri(name):
    """take the name of a song and return its uri"""
    url = f"https://api.spotify.com/v1/search?q={name}&type=track"

    payload = {}
    headers = {"Authorization": f"Bearer {refreshed_token()}"}

    response = requests.request("GET", url, headers=headers, data=payload)
    response_json = response.json()
    song_found = response_json["tracks"]["items"]
    if not song_found:
        # play a funny sound if the song is not found
        playsound.playsound("./media/pas_trouve.mp3")
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
    playsound.playsound("./media/ca_degage.mp3")


def add_track_to_playback(song_uri):
    url = f"https://api.spotify.com/v1/me/player/queue?uri={song_uri}"

    payload = {}
    headers = {"Authorization": f"Bearer {refreshed_token()}"}

    response = requests.request("POST", url, headers=headers, data=payload)


def play_music_requested(user_input):
    add_track_to_playback(

        get_track_uri(user_input),
    )


@route('/currently_playing')
def get_currently_played():
    url = "https://api.spotify.com/v1/me/player/currently-playing"

    payload = {}
    headers = {
        'Authorization': f'Bearer {request.get_header("token")}',
        'Access-Control-allow-Origin': '*'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response = response.text
    return json.loads(response)



@route('/static/<filename>')
def get_static(filename):
    return static_file(filename, root='music_player')


def run_server():
    run(host='localhost', port=8080)


Thread(target=run_server).start()
