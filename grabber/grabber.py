import datetime
import json
import math
import os
import socket
import time

from ossapi import OssapiV1

from utils import get_absolute_path, sign

from .lobby import Lobby

SERVER = "irc.ppy.sh"
PORT = 6667


class Grabber:
    def __init__(self, osu_api_v1: OssapiV1) -> None:
        self.api = osu_api_v1

        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.username = os.environ.get("OSU_USERNAME")
        self.password = os.environ.get("OSU_IRC_PASSWORD")

        self._latest_lobby = self._get_latest_local_lobby()

    def _connect(self):
        self.irc.connect((SERVER, PORT))
        self.irc.send(f"PASS {self.password}\r\n".encode())
        self.irc.send(f"NICK {self.username}\r\n".encode())
        self.irc.send(f"USER {self.username} 0 * :{self.username}\r\n".encode())

    def _disconnect(self):
        self.irc.send(f"QUIT\r\n".encode())
        self.irc.close()

    def find_id(self, timestamp: datetime.datetime):
        latest_lobby = self._get_latest_local_lobby()

        if latest_lobby.timestamp < timestamp:
            latest_lobby = self._get_latest_live_lobby()

        FIFTEEN_MINUTES = 60 * 15

        # while True:
        #     try:
        #         delta_id = 15000
        #         guess_id = latest_lobby.mp_id - delta_id
        #         guess = self.api.get_match(guess_id)
        #         break
        #     except:
        #         delta_id += 1

        # while True:
        #     guess_time: datetime.datetime = guess.match.start_time  # type: ignore
        #     delta_time = (latest_lobby.timestamp - guess_time).total_seconds()

        #     if (timestamp - guess_time).total_seconds() < FIFTEEN_MINUTES:

        #     slope = delta_id / delta_time

        #     delta_id = int(slope * (latest_lobby.timestamp - timestamp).total_seconds())
        #     guess_id -= delta_id
        #     while True:
        #         try:
        #             guess = self.api.get_match(guess_id)
        #             break
        #         except:
        #             guess_id -= sign(delta_id)

    def _get_latest_local_lobby(self) -> Lobby:
        with open(get_absolute_path(__file__, "latest_local_lobby.json")) as log_file:
            latest_local_lobby = json.load(log_file)

        return Lobby(**latest_local_lobby)

    def _get_latest_live_lobby(
        self, lobby_name: str = "tja", timeout: int = 10
    ) -> Lobby:
        self.irc.send(f"PRIVMSG BanchoBot :!mp make {lobby_name}\r\n".encode())
        start_time = time.time()

        while True:
            if (time.time() - start_time) > timeout:
                raise TimeoutError(
                    "Osu IRC took too long to create a lobby. (or something else happened)"
                )
            text = self.irc.recv(2040).decode()
            # if "QUIT" in text:
            #     continue
            if "https://osu.ppy.sh/mp/" in text:
                return Lobby(
                    datetime.datetime.now(datetime.UTC).isoformat(),
                    int(text.split("https://osu.ppy.sh/mp/")[1].split(" ")[0]),
                )

    def __enter__(self):
        self._connect()
        return self

    def __exit__(self, *_):
        self._disconnect()


# irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# username = ""
# password = ""

# irc.connect((server, port))

# try:

# except KeyboardInterrupt:
#     irc.send(f"QUIT\r\n".encode())

# # irc.send(f"\r\n".encode())
