import json
import requests
from dotenv import load_dotenv
import os
import playsound
from bottle import route, run, static_file, request
from datetime import datetime
from threading import Thread

load_dotenv()

ACCESS_TOKEN = None
LAST_TIME_REFRESH = None


def write_files(filename, values, keys, overwrite=False):
    if not os.path.isfile(filename) or overwrite == True:
        with open(filename, "w") as f:
            for i in range(len(values)):
                f.write(keys[i] + ";" + values[i] + "\n")
            f.close()



def read_informations(filename, key):
    informations = {}
    if os.path.isfile(filename):
        with open(filename, "r") as f:
            for line in f:
                split_line = line.split(";")
                if len(split_line) == 2:
                    informations[split_line[0]] = split_line[1].strip("\n")
            f.close()
            if key in informations:
                return informations[key]
            return None
    else:
        return None


def refreshed_token(is_init=True):
    global ACCESS_TOKEN
    global LAST_TIME_REFRESH

    # execute this if code when true
    if is_init:
        LAST_TIME_REFRESH = datetime.now()
        url = "https://accounts.spotify.com/api/token"

        payload = (
            f'grant_type=refresh_token&refresh_token={read_informations("music_player/spotify_informations.txt" ,"refresh_token")}'
            f'&client_id={read_informations("music_player/spotify_informations.txt" ,"client_id")}'
        )
        headers = {
            "Authorization": f'Basic {read_informations("music_player/spotify_informations.txt" ,"spotify_base_64")}',
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        if "error" in response:
            return None
        ACCESS_TOKEN = response["access_token"]
        return ACCESS_TOKEN
    # execute this code when false
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
        playsound.playsound("./media/not_found_sounds/no_found_sound_1.mp3")
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
    playsound.playsound("./media/skip_sounds/skip_sound_1.mp3")


def add_track_to_playback(song_uri):
    url = f"https://api.spotify.com/v1/me/player/queue?uri={song_uri}"

    payload = {}
    headers = {"Authorization": f"Bearer {refreshed_token()}"}

    response = requests.request("POST", url, headers=headers, data=payload)


def play_music_requested(user_input):
    add_track_to_playback(
        get_track_uri(user_input),
    )


@route("/currently_playing")
def get_currently_played():
    url = "https://api.spotify.com/v1/me/player/currently-playing"

    payload = {}
    headers = {
        "Authorization": f"Bearer {refreshed_token()}",
        "Access-Control-allow-Origin": "*",
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response = response.text

    return json.loads(response)


@route("/<filename>")
def get_static(filename):
    return static_file(filename, root="music_player")


@route("/")
def get_started():
    return static_file("home.html", root="")


@route("/spotify")
def get_started_spotify():
    return static_file("step_1.html", root="spotify/steps")


@route("/static_spotify/<filename>")
def get_static(filename):
    return static_file(filename, root="spotify/steps")


@route("/callbackspotify")
def get_callback_spotify():
    return static_file("step_2.html", root="spotify/steps")


@route("/static_twitch/<filename>")
def get_static_twitch(filename):
    return static_file(filename, root="twitch/steps")


@route("/twitch")
def get_started_twitch():
    return static_file("step_1.html", root="twitch/steps")


@route("/callbacktwitch")
def get_callback_twitch():
    return static_file("step_2.html", root="twitch/steps")


@route("/store_informations_spotify")
def store_informations_spotify():
    refresh_token = request.get_header("token")
    client_id = request.get_header("client_id")
    spotify_base_64 = request.get_header("Spotify_base_64")
    write_files(
        "music_player/spotify_informations.txt",
        [refresh_token, client_id, spotify_base_64],
        ["refresh_token", "client_id", "spotify_base_64"],
    )
    return f"informations from spotify received"


@route("/store_informations_twitch")
def store_informations_twitch():
    reward_id = request.get_header("rewardId")
    reward_type = request.get_header("rewardType")
    write_files(f"twitch_pubsub/{reward_type}_informations.txt", [reward_id], ["Id"])
    return f"informations from twitch received"


def run_server():
    run(host="localhost", port=8080)


Thread(target=run_server).start()
