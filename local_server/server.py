# import json
# import requests
# import playsound
# from bottle import route, run, static_file, request
# from datetime import datetime
# from threading import Thread
# import os
# from spotify import spotify
#
#
#
#
#
#
#
#
#
#
# @route("/currently_playing")
# def get_currently_played():
#     url = "https://api.spotify.com/v1/me/player/currently-playing"
#
#     payload = {}
#     headers = {
#         "Authorization": f"Bearer {spotify.refreshed_token()}",
#         "Access-Control-allow-Origin": "*",
#     }
#     response = requests.request("GET", url, headers=headers, data=payload)
#     response.headers["Access-Control-Allow-Origin"] = "*"
#     response = response.text
#
#     return json.loads(response)
#
#
# @route("/<filename>")
# def get_static(filename):
#     return static_file(filename, root="music_player")
#
#
# @route("/")
# def get_started():
#     return static_file("home.html", root="")
#
#
# @route("/spotify")
# def get_started_spotify():
#     return static_file("step_1.html", root="spotify/steps")
#
#
# @route("/static_spotify/<filename>")
# def get_static(filename):
#     return static_file(filename, root="spotify/steps")
#
#
# @route("/callbackspotify")
# def get_callback_spotify():
#     return static_file("step_2.html", root="spotify/steps")
#
#
# @route("/static_twitch/<filename>")
# def get_static_twitch(filename):
#     return static_file(filename, root="twitch/steps")
#
#
# @route("/twitch")
# def get_started_twitch():
#     return static_file("step_1.html", root="twitch/steps")
#
#
# @route("/callbacktwitch")
# def get_callback_twitch():
#     return static_file("step_2.html", root="twitch/steps")
#
#
# @route("/store_informations_spotify")
# def store_informations_spotify():
#     refresh_token = request.get_header("token")
#     client_id = request.get_header("client_id")
#     spotify_base_64 = request.get_header("Spotify_base_64")
#     spotify.write_files(
#         "music_player/spotify_informations.txt",
#         [refresh_token, client_id, spotify_base_64],
#         ["refresh_token", "client_id", "spotify_base_64"],
#     )
#     return f"informations from spotify received"
#
#
# @route("/store_informations_twitch")
# def store_informations_twitch():
#     reward_id = request.get_header("rewardId")
#     reward_type = request.get_header("rewardType")
#     spotify.write_files(f"twitch_pubsub/{reward_type}_informations.txt", [reward_id], ["Id"])
#     return f"informations from twitch received"
#
#
# def run_server():
#     run(host="localhost", port=8080)
#
#
# Thread(target=run_server).start()