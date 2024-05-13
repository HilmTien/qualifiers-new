import datetime
import json
import os
import socket
import time

from ossapi import OssapiV1

from utils import get_absolute_path, sign

from .lobby import Lobby

IRC_SERVER = "irc.ppy.sh"
IRC_PORT = 6667


class LiveGrabber:
    def __init__(self, osu_api_v1: OssapiV1) -> None:
        self.api = osu_api_v1

        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.username = os.environ.get("OSU_USERNAME")
        self.password = os.environ.get("OSU_IRC_PASSWORD")

    def get_latest_live_lobby(
        self, lobby_name: str = "tja", timeout: int = 10, save: bool = True
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
            # print(text)
            if "https://osu.ppy.sh/mp/" in text:
                lobby_data = {
                    "timestamp_raw": datetime.datetime.now(datetime.UTC).isoformat(),
                    "mp_id": int(text.split("https://osu.ppy.sh/mp/")[1].split(" ")[0]),
                }
                if save:
                    with open(
                        get_absolute_path(__file__, "latest_local_lobby.json"), "w"
                    ) as log_file:
                        json.dump(lobby_data, log_file)
                self.irc.send(
                    f"PRIVMSG #mp_{lobby_data['mp_id']} :!mp close\r\n".encode()
                )
                return Lobby(**lobby_data)

    def _connect(self):
        self.irc.connect((IRC_SERVER, IRC_PORT))
        self.irc.send(f"PASS {self.password}\r\n".encode())
        self.irc.send(f"NICK {self.username}\r\n".encode())
        self.irc.send(f"USER {self.username} 0 * :{self.username}\r\n".encode())

    def _disconnect(self):
        self.irc.send(f"QUIT\r\n".encode())
        self.irc.close()

    def __enter__(self):
        self._connect()
        return self

    def __exit__(self, *_):
        self._disconnect()
