import json
import os
from collections import defaultdict
from datetime import datetime, timedelta

from custom_types import JSON, BeatmapID, Scoring
from ruleset import GameMode, Ruleset
from utils import get_absolute_path

# TOURNAMENT INFO
TOURNAMENT_NAME = "btt-2024"
ACRONYM = "BTTS9"
RULESET = Ruleset(gamemode=GameMode.TAIKO, teams=False, required_runs=1, runs=2, must_be_complete=False)


# DATA FILES
DATA_PATH = get_absolute_path(__file__, "tournament_data", TOURNAMENT_NAME)

# REQUIRED
MAPPOOL_FILE = "mappool.json"
SCHEDULE_FILE = "schedule.json"

# GENERATED
ID_USERNAME_MAPPING_FILE = "players.json"
RESULTS_FILE = "results.json"
COMPLETED_FILE = "lobbies.json"
PARTIALS_FILE = "partials.json"
PARTIAL_FAULTS_FILE = "faults.json"
FAILED_FILE = "failed.json"
LOG_FILE = f"log-{datetime.now().strftime("%Y.%m.%d-%H.%M.%S")}.txt"


# SEARCH BEHAVIOUR
TIME_BEFORE_SCHEDULE = timedelta(minutes=15)
MAX_TIME_AFTER_SCHEDULE = timedelta(minutes=10)
CAN_GRAB_LIVE_LOBBY = False


# PARSE BEHAVIOUR
USE_USERNAME = True
LOAD_LOCAL_RESULTS = True
USE_LOCAL_ONLY = True

# ----- UTILS -----


def get_path(file: str) -> str:
    return os.path.join(DATA_PATH, file)


def get_data(file: str) -> JSON:
    with open(get_path(file)) as f:
        return json.load(f)


def get_mappool_info() -> tuple[set[BeatmapID], dict[str, BeatmapID] | list[BeatmapID]]:
    mappool = get_data(MAPPOOL_FILE)
    match mappool:
        case list():
            return set(mappool), mappool
        case dict():
            return set(mappool.values()), mappool

    raise TypeError(
        "Unexpected mappool format. Should be list of beatmap IDs or dict of index: ID"
    )


def blank_user_scoring() -> Scoring:
    mappool, _ = get_mappool_info()
    blank_mappool_scoring = {beatmap: 0 for beatmap in mappool}
    return defaultdict(lambda: blank_mappool_scoring.copy())
