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

        initial_guess = self._get_initial_guess(latest_lobby)

        self._search_id(initial_guess, latest_lobby, timestamp)

    def _get_initial_guess(self, initial_lobby: Lobby):
        while True:
            try:
                delta_id = 15000
                guess_id = initial_lobby.mp_id - delta_id
                guess = self.api.get_match(guess_id)
                return Lobby(guess.match.start_time.isoformat(), guess_id)
            except:
                delta_id += 1

    def _search_id(
        self, left_lobby: Lobby, right_lobby: Lobby, lookup_time: datetime.datetime
    ) -> int:
        while True:
            delta_id = right_lobby.mp_id - left_lobby.mp_id
            delta_time = (right_lobby.timestamp - left_lobby.timestamp).total_seconds()

            slope = delta_id / delta_time  # positive direction: left

            delta_time_lookup = (right_lobby.timestamp - lookup_time).total_seconds()

            slope * delta_time_lookup

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
