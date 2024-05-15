import datetime
import json

from ossapi.ossapi import MatchGame, MatchInfo, MatchScore, OssapiV1

from custom_types import Scoring
from settings import ACRONYM, MAPPOOL_FILE, blank_user_scoring, get_data
from utils import get_absolute_path

from .live_grabber import LiveGrabber
from .lobby import Lobby
from .tourney_lobby import CompleteLobby, PartialLobby, TournamentLobby

SERVER = "irc.ppy.sh"
PORT = 6667


class Grabber:
    def __init__(
        self,
        osu_api_v1: OssapiV1,
        can_grab_live_lobby: bool = True,
    ) -> None:
        self.api = osu_api_v1
        self.acronym = ACRONYM.lower()

        self.has_grabbed_live_lobby = not can_grab_live_lobby

    def find_lobby(
        self,
        scheduled_time: datetime.datetime,
        start_id: int,
        stop_time_offset: datetime.timedelta = datetime.timedelta(minutes=20),
    ) -> TournamentLobby:
        mp_id = start_id
        while True:
            try:
                data = self.api.get_match(mp_id)
            except TypeError:
                # print("skipped", mp_id, "due to denied access")
                mp_id += 1
                continue

            if data.match.start_time > (scheduled_time + stop_time_offset):
                raise LookupError("no lobby was found")

            lobby_name: str = data.match.name
            print(lobby_name, mp_id, data.match.start_time)

            index = lobby_name.lower().find(self.acronym)
            if index == 0:
                return self._return_lobby(data)
            elif index > 0:
                print(f"sus: {mp_id} ({data.match.name})")
                if input("verify id (y / n)").lower() == "y":
                    return self._return_lobby(data)

            mp_id += 1

    # UNUSED for now because most lobbies dont get separated

    # def find_lobby_partial(
    #     self,
    #     partial_match: Match,
    #     stop_time_offset: datetime.timedelta = datetime.timedelta(minutes=5),
    # ) -> list[int]:
    #     return [
    #         partial_match.match_id,
    #     ] + self.find_lobby(
    #         partial_match.start_time,
    #         partial_match.match_id + 1,
    #         (partial_match.end_time - partial_match.start_time) + stop_time_offset,
    #     )

    def _return_lobby(self, lobby: MatchInfo) -> TournamentLobby:
        if self.lobby_is_complete(lobby):
            return CompleteLobby(lobby)

        faults = self._filter_faulty_runs(self.played_maps_count(lobby.games))
        return PartialLobby(lobby, faults)

    def _filter_faulty_runs(self, played_maps_count: Scoring) -> Scoring:
        return {
            user_id: play_count
            for user_id, play_count in played_maps_count.items()
            if 0 in play_count.values()
        }

    def played_maps_count(self, games: list[MatchGame]) -> Scoring:
        mappool: list[int] = get_data(MAPPOOL_FILE)
        played = blank_user_scoring()

        for game in games:
            scores: list[MatchScore] = game.scores

            if game.beatmap_id not in mappool:
                continue

            for score in scores:
                played[score.user_id][game.beatmap_id] += 1

        return played

    def lobby_is_complete(self, lobby: MatchInfo) -> bool:
        played = self.played_maps_count(lobby.games)

        return False if self._filter_faulty_runs(played) else True

    def find_id(
        self,
        lookup: datetime.datetime,
        initial_delta_id: int = 15000,
        precision: float = 60,
    ) -> int:
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
            except TypeError:
                delta_id += 1

    def _calc_id_slope(self, lobby_1: Lobby, lobby_2: Lobby):
        delta_id = lobby_2.mp_id - lobby_1.mp_id
        delta_time = (lobby_2.timestamp - lobby_1.timestamp).total_seconds()

        return delta_id / delta_time

    def _get_latest_local_lobby(self) -> Lobby:
        with open(get_absolute_path(__file__, "latest_local_lobby.json")) as log_file:
            latest_local_lobby = json.load(log_file)

        return Lobby(**latest_local_lobby)
