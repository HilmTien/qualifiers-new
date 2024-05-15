from functools import cached_property

import pandas as pd
from ossapi import OssapiV1
from ossapi.models import MatchGame

from settings import RULESET, blank_user_scoring, get_mappool_info
from utils import apply_fr


class Tournament:
    def __init__(self, osu_api_v1: OssapiV1, mp_ids: list[int], use_username: bool = False) -> None:
        self.api = osu_api_v1
        self.mp_ids = mp_ids
        self.use_username = use_username

        self.mappool, self.alias_mapping = get_mappool_info()

        # TODO: UNIMPLEMENTED
        # self.teams: dict[str, str]  # player: team?

    @cached_property
    def results(self) -> pd.DataFrame:
        results = blank_user_scoring()
        for mp_id in self.mp_ids:
            mp_data: list[MatchGame] = self.api.get_match(mp_id).games

            for beatmap in mp_data:
                beatmap_id = beatmap.beatmap_id

                if beatmap_id not in self.mappool:
                    continue

                for score in beatmap.scores:
                    player_name = score.user_id
                    if self.use_username:
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
        return self.results.rank(axis=1, method="min", ascending=False).T.astype(int)

    def get_overall_results(self) -> pd.Series:
        return self.get_placements().sum(axis=1).rank()

    def get_required_score(self, index: str | int, placement: int) -> int:
        match index:
            case int():
                if index not in self.mappool:
                    print(f"Invalid index passed. Index should be in: {", ".join(self.mappool)}")
                    return -1
                
                series = self.results.T[index]
            case str():
                if isinstance(self.alias_mapping, list):
                    print("Cannot pass alias when the mappool is a list.")
                    return -1

                if index not in self.alias_mapping:
                    print(f"Invalid index passed. Index should be in: {", ".join(self.alias_mapping)}")
                    return -1
                
                series = self.results.T[self.alias_mapping[index]]

        if placement < 1:
            print("Placement cannot be below 1.")
            return -1
        
        return series.nlargest(placement).iloc[-1]
    
    def get_scores_for_seed(self, seed: int, distribution: list[float]) -> list[int]:
        if len(distribution) != len(self.mappool):
            print("Too few or too many points in distribution")
            return [-1] * len(self.mappool)

        seed_below_points = self.get_placements().sum(axis=1).nsmallest(seed).iloc[-1]
        if seed < 1:
            print("Seed cannot be lower than 1")
            return [-1] * len(self.mappool)
        elif seed == 1:
            seed_points = (seed_below_points + len(self.mappool)) // 2
        elif 1 < seed <= len(self.results.columns):
            seed_points = (seed_below_points + self.get_placements().sum(axis=1).nsmallest(seed).iloc[-2]) // 2
        else:
            seed_points = (seed_below_points + len(self.mappool) * (len(self.results.columns) + 1)) // 2

        map_placements = apply_fr(distribution, seed_points)
        print(seed_points, map_placements, sum(map_placements))
        scores = []

        match self.alias_mapping:
            case dict(): mappool = self.alias_mapping.values()
            case list(): mappool = self.alias_mapping

        for placement, map_id in zip(map_placements, mappool):
            print(placement, map_id)
            scores.append(self.results.T[map_id].nlargest(placement).iloc[-1])
        
        return scores

