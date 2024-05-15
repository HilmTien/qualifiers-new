import json
import os
from collections import defaultdict
from datetime import timedelta
from typing import Any

from custom_types import Scoring
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


def get_data(file: str) -> Any:
    with open(get_path(file)) as f:
        return json.load(f)


def blank_user_scoring() -> Scoring:
    mappool: list[int] = get_data(MAPPOOL_FILE)
    blank_mappool_scoring = {beatmap: 0 for beatmap in mappool}
    return defaultdict(lambda: blank_mappool_scoring.copy())
