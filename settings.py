import json
import os
from collections import defaultdict
from datetime import timedelta

from custom_types import JSON, BeatmapID, Scoring
from ruleset import Ruleset
from utils import get_absolute_path

# TOURNAMENT INFO

TOURNAMENT_NAME = "o!nt-4"
ACRONYM = "o!nt"
RULESET = Ruleset(teams=False, required_runs=1, runs=2)


# DATA FILES

DATA_PATH = get_absolute_path(__file__, "tournament_data", TOURNAMENT_NAME)

# REQUIRED
MAPPOOL_FILE = "mappool.json"
SCHEDULE_FILE = "schedule.json"

# GENERATED
COMPLETED_FILE = "lobbies.json"
PARTIALS_FILE = "partials.json"
FAILED_FILE = "failed.json"
LOG_FILE = "log.txt"


# SEARCH BEHAVIOUR

TIME_BEFORE_SCHEDULE = timedelta(minutes=15)
MAX_TIME_AFTER_SCHEDULE = timedelta(minutes=10)


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
