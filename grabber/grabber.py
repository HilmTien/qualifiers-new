import datetime
import json

from ossapi import OssapiV1

from utils import get_absolute_path

from .live_grabber import LiveGrabber
from .lobby import Lobby

SERVER = "irc.ppy.sh"
PORT = 6667


class Grabber:
    def __init__(
        self,
        osu_api_v1: OssapiV1,
        tournament_acronym: str = None,
        can_grab_live_lobby: bool = True,
    ) -> None:
        self.api = osu_api_v1
        self.acronym = tournament_acronym.lower() if tournament_acronym else None

        self.has_grabbed_live_lobby = not can_grab_live_lobby

    def find_lobby(
        self,
        scheduled_time: datetime.datetime,
        start_id: int,
        stop_time_offset: datetime.timedelta = datetime.timedelta(minutes=20),
    ) -> int:
        if self.acronym is None:
            raise ValueError("Tournament acronym for grabber is not set!")

        mp_id = start_id
        while True:
            try:
                data = self.api.get_match(mp_id)
            except KeyboardInterrupt:
                return -1
            except:
                print("skipped", mp_id, "due to denied access")
                mp_id += 1
                continue

            if data.match.start_time > (scheduled_time + stop_time_offset):
                raise LookupError("no lobby was found")

            lobby_name: str = data.match.name
            print(lobby_name, mp_id, data.match.start_time)

            index = lobby_name.lower().find(self.acronym)
            if index == 0:
                return mp_id
            elif index > 0:
                print("sus: " + mp_id)
                if input("verify id (y/n)").lower() == "y":
                    return mp_id

            mp_id += 1

    def find_id(
        self,
        lookup: datetime.datetime,
        initial_delta_id: int = 15000,
        precision: float = 60,
    ):
        latest_lobby = self._get_latest_local_lobby()

        if latest_lobby.timestamp < lookup and not self.has_grabbed_live_lobby:
            with LiveGrabber(self.api) as live_grabber:
                latest_lobby = live_grabber.get_latest_live_lobby()

            self.has_grabbed_live_lobby = True

        guess = self._get_guess(latest_lobby.mp_id, initial_delta_id)
        delta_time = (guess.timestamp - lookup).total_seconds()

        while abs(delta_time) > precision:
            slope = self._calc_id_slope(guess, latest_lobby)
            delta_id = int(slope * delta_time)

            latest_lobby = guess

            guess = self._get_guess(latest_lobby.mp_id, delta_id)
            delta_time = (guess.timestamp - lookup).total_seconds()

        return guess.mp_id

    def _get_guess(self, right_id: int, delta_id: int):
        while True:
            try:
                guess_id = right_id - delta_id
                guess = self.api.get_match(guess_id)
                return Lobby(guess.match.start_time.isoformat(), guess_id)
            except:
                delta_id += 1

    def _calc_id_slope(self, lobby_1: Lobby, lobby_2: Lobby):
        delta_id = lobby_2.mp_id - lobby_1.mp_id
        delta_time = (lobby_2.timestamp - lobby_1.timestamp).total_seconds()

        return delta_id / delta_time

    def _get_latest_local_lobby(self) -> Lobby:
        with open(get_absolute_path(__file__, "latest_local_lobby.json")) as log_file:
            latest_local_lobby = json.load(log_file)

        return Lobby(**latest_local_lobby)
