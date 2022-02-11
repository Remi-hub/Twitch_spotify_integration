import asyncio
from twitch_pubsub.webSocketClient import WebSocketClient
from twitch_pubsub.webSocketClient import refreshed_access_token
import os
import time

if __name__ == "__main__":

    # Creating client object
    file_created = False
    while not file_created:
        file_created = os.path.isfile(
            "twitch_pubsub/broadcaster_id_informations.txt"
        ) and os.path.isfile("twitch_pubsub/twitch_access_token_informations.txt")
        time.sleep(5)
    counter = 0
    while True:
        refreshed_access_token()
        client = WebSocketClient()
        loop = asyncio.get_event_loop()
        # Start connection and get client connection protocol
        connection = loop.run_until_complete(client.connect())
        # Start listener and heartbeat
        tasks = [
            asyncio.ensure_future(client.heartbeat(connection)),
            asyncio.ensure_future(client.receiveMessage(connection)),
        ]

        loop.run_until_complete(asyncio.wait(tasks))

        print("disconnected... reconnecting...")
