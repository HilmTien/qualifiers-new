import json
from functools import cached_property

import pandas as pd
from ossapi import OssapiV1
from ossapi.models import MatchGame

from settings import (
    ID_USERNAME_MAPPING_FILE,
    LOAD_LOCAL_RESULTS,
    PARTIAL_FAULTS_FILE,
    RESULTS_FILE,
    RULESET,
    USE_LOCAL_ONLY,
    USE_USERNAME,
    blank_user_scoring,
    get_data,
    get_mappool_info,
    get_path,
)
from utils import apply_fr, get_scoring_from_json


class Tournament:
    def __init__(
        self,
        osu_api_v1: OssapiV1,
        mp_ids: list[int]
    ) -> None:
        self.api = osu_api_v1
        self.mp_ids = mp_ids

        self._id_results = None

        self.mappool, self.mappool_json = get_mappool_info()

        # TODO: UNIMPLEMENTED
        # self.teams: dict[str, str]  # player: team?

    @cached_property
    def results(self) -> pd.DataFrame:
        results = blank_user_scoring()

        if LOAD_LOCAL_RESULTS:
            local_results = get_data(RESULTS_FILE)
            results.update(get_scoring_from_json(local_results))
            
        for mp_id in self.mp_ids:
            if USE_LOCAL_ONLY:
                break

            mp_data: list[MatchGame] = self.api.get_match(mp_id).games

            for beatmap in mp_data:
                beatmap_id = beatmap.beatmap_id

                if beatmap_id not in self.mappool:
                    continue

                for score in beatmap.scores:
                    player_name = score.user_id

                    if RULESET.must_be_complete and player_name in get_data(PARTIAL_FAULTS_FILE):
                        continue

                    if not RULESET.teams:
                        results[player_name][beatmap_id] = max(
                            results[player_name][beatmap_id], score.score
                        )

                    # TODO: TEAMS
                    # for team, players in teams.items():
                    #     if player_name in players:
                    #         res[team][beatmap_id] += int(score["score"])

        if USE_USERNAME:
            id_results = results
            self._id_results = pd.DataFrame(id_results)

            results = {}
            id_username_map = get_data(ID_USERNAME_MAPPING_FILE)
            for user, scoring in id_results.items():
                if str(user) in id_username_map:
                    username = id_username_map[str(user)]
                else:
                    username = self.api.get_user(user, user_type="id", mode=RULESET.gamemode).username
                    id_username_map[str(user)] = username 

                results[username] = scoring

            with open(get_path(ID_USERNAME_MAPPING_FILE), "w") as players_file:
                json.dump(id_username_map, players_file)

        return pd.DataFrame(results)

    def get_placements(self) -> pd.DataFrame:
        return self.results.rank(axis=1, method="min", ascending=False).T.astype(int)

    def get_overall_results(self) -> pd.Series:
        return self.get_placements().sum(axis=1).rank().sort_values()

    def get_required_score(self, index: str | int, placement: int) -> int:
        match index:
            case int():
                if index not in self.mappool:
                    print(f"Invalid index passed. Index should be in: {", ".join(self.mappool)}")
                    return -1
                
                series = self.results.T[index]
            case str():
                if isinstance(self.mappool_json, list):
                    print("Cannot pass alias when the mappool is a list.")
                    return -1

                if index not in self.mappool_json:
                    print(f"Invalid index passed. Index should be in: {", ".join(self.mappool_json)}")
                    return -1
                
                series = self.results.T[self.mappool_json[index]]

        if placement < 1:
            print("Placement cannot be below 1.")
            return -1
        
        return series.nlargest(placement).iloc[-1]
    
    def get_scores_for_seed(self, seed: int, distribution: list[float] | dict[str, float]) -> list[int]:
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
        # print(seed_points, map_placements, sum(map_placements))

        print(f"Using weights: {map_placements}")

        match map_placements:
            case dict():
                return {
                    map_alias: self.results.T[self.mappool_json[map_alias]].nlargest(placement).iloc[-1]
                    for map_alias, placement in map_placements.items()
                    }
            case list():
                return [
                    self.results.T[map_id].nlargest(placement).iloc[-1] for placement, map_id in zip(map_placements, self.mappool_json)
                ]

    def save_results(self) -> None:
        if self._id_results is None:
            self.results.to_json(get_path(RESULTS_FILE))
        else:
            self._id_results.to_json(get_path(RESULTS_FILE))
