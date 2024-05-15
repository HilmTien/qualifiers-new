import pandas as pd
from ossapi import OssapiV1
from ossapi.models import MatchGame

from settings import MAPPOOL_FILE, RULESET, blank_user_scoring, get_data


class Tournament:
    def __init__(self, osu_api_v1: OssapiV1, mp_ids: list[int]) -> None:
        self.api = osu_api_v1
        self.mp_ids = mp_ids

        self.results = self.get_results()

        # TODO: UNIMPLEMENTED
        # self.teams: dict[str, str]  # player: team?

    def get_results(self) -> pd.DataFrame:
        mappool: list[int] = get_data(MAPPOOL_FILE)
        results = blank_user_scoring()
        for mp_id in self.mp_ids:
            mp_data: list[MatchGame] = self.api.get_match(mp_id).games

            for beatmap in mp_data:
                beatmap_id = beatmap.beatmap_id

                if beatmap_id not in mappool:
                    continue

                for score in beatmap.scores:
                    player_name = self.api.get_user(
                        score.user_id, user_type="id"
                    ).username

                    if not RULESET.teams:
                        results[player_name][beatmap_id] = max(
                            results[player_name][beatmap_id], score.score
                        )

                    # TODO: TEAMS
                    # for team, players in teams.items():
                    #     if player_name in players:
                    #         res[team][beatmap_id] += int(score["score"])

        return pd.DataFrame(results)

    def get_placements(self) -> pd.DataFrame:
        return self.results.rank(axis=1, ascending=False).T

    def get_overall_results(self) -> pd.Series:
        return self.get_placements().sum(axis=1).rank()
