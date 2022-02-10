import websockets
import asyncio
import uuid
import json
import os
from dotenv import load_dotenv
from spotify import spotify

load_dotenv()

TWITCH_TOKEN = os.getenv("TWITCH_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")


def get_user_input(response):
    response = response["data"]["message"]
    response = json.loads(response)
    if "user_input" in response["data"]["redemption"]:
        message = response["data"]["redemption"]["user_input"]
        return message
    else:
        return None


def print_user_name_and_input(name, input):
    return print(f"{name} requested {input}")


def get_reward_id(response):
    message_in_response = response["data"]["message"]
    message_in_response = json.loads(message_in_response)
    reward_id = message_in_response["data"]["redemption"]["reward"]["id"]
    print(reward_id)
    return reward_id


class WebSocketClient:
    def __init__(self):
        # list of topics to subscribe to
        self.topics = [f"channel-points-channel-v1.{spotify.read_informations('twitch_pubsub/broadcaster_id_informations.txt', 'Id')}"]
        self.auth_token = f"{spotify.read_informations('twitch_pubsub/twitch_access_token_informations.txt', 'Id')}"


    async def connect(self):
        """
        Connecting to webSocket server
        websockets.client.connect returns a WebSocketClientProtocol,
        which is used to send and receive messages
        """
        self.connection = await websockets.connect("wss://pubsub-edge.twitch.tv")
        if self.connection.open:
            print("Connection stablished. Client correcly connected")
            # Send greeting
            message = {
                "type": "LISTEN",
                "nonce": str(self.generate_nonce()),
                "data": {"topics": self.topics, "auth_token": self.auth_token},
            }
            json_message = json.dumps(message)
            await self.sendMessage(json_message)
            return self.connection


    def generate_nonce(self):
        """Generate pseudo-random number and seconds since epoch (UTC)."""
        nonce = uuid.uuid1()
        oauth_nonce = nonce.hex
        return oauth_nonce

    async def sendMessage(self, message):
        """Sending message to webSocket server"""
        await self.connection.send(message)

    async def receiveMessage(self, connection):
        """Receiving all server messages and handling them"""
        while True:
            try:
                message = await connection.recv()
                print("Received message from server: " + str(message))
                response = json.loads(message)

                if "data" in response:
                    message_in_response = response["data"]["message"]
                    message_in_response = json.loads(message_in_response)
                    claimed_reward_id = message_in_response["data"]["redemption"]["reward"]["id"]
                    # if the requested id matches the following ids:

                    # play requested song :
                    if claimed_reward_id == spotify.read_informations("twitch_pubsub/Request_Song_informations.txt", "Id"):
                        print("LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL")
                        print(claimed_reward_id)
                        print(spotify.read_informations("Request_Song_informations.txt", "Id"))
                    # if claimed_reward_id == "86fab6d6-09f5-4506-a172-9dfb2a750aae":
                        spotify.play_music_requested(get_user_input(response))


                    # skip the current song :
                    elif claimed_reward_id == spotify.read_informations("twitch_pubsub/Skip_current_song_informations.txt", "Id"):
                    # elif claimed_reward_id == "3d9b655e-9ddc-483a-9891-488ce9883ac7":
                        spotify.skip_current_track()

            except websockets.exceptions.ConnectionClosed:
                print("Connection with server closed")
                break

    async def heartbeat(self, connection):
        """
        Sending heartbeat to server every 1 minutes
        Ping - pong messages to verify/keep connection is alive
        """
        while True:
            try:
                data_set = {"type": "PING"}
                json_request = json.dumps(data_set)
                # print(json_request)
                await connection.send(json_request)
                await asyncio.sleep(60)
            except websockets.exceptions.ConnectionClosed:
                print("Connection with server closed")
                break
