import os
from collections import defaultdict

from ossapi import OssapiV1
from ossapi.models import MatchGame

from settings import SETTINGS


class Tournament:
    def __init__(self, osu_api_v1: OssapiV1, mp_ids: list[int]) -> None:
        self.api = osu_api_v1
        self.mp_ids = mp_ids

        # TODO: UNIMPLEMENTED
        # self.teams: dict[str, str]  # player: team?

    def generate_results(self):
        results = defaultdict(lambda: defaultdict(int))
        for mp_id in self.mp_ids:
            mp_data: list[MatchGame] = self.api.get_match(mp_id).games

            for beatmap in mp_data:
                beatmap_id = beatmap.beatmap_id

                for score in beatmap.scores:
                    player_name = self.api.get_user(
                        score.user_id, user_type="id"
                    ).username

                    if not SETTINGS.ruleset.teams:
                        results[player_name][beatmap_id] = max(
                            results[player_name][beatmap_id], score.score
                        )

                    # TODO: TEAMS
                    # for team, players in teams.items():
                    #     if player_name in players:
                    #         res[team][beatmap_id] += int(score["score"])

        return results
