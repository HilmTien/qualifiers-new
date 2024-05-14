import json
from typing import Any, Final

from qualifiers.tourney_ruleset import Ruleset
from utils import get_absolute_path

SETTINGS: Final[dict[str, Any]] = {
    "data_path": get_absolute_path(__file__, "tournament_data"),
    "mappool_file": "mappool.json",
    "ruleset": Ruleset(teams=False, required_runs=1, runs=2),
    "tournament_name": "prism-2024",
    "acronym": "prism",
}

# ----- UTILS -----


def get_mappool() -> list[int]:
    with open(
        get_absolute_path(SETTINGS["data_path"], SETTINGS["mappool_file"])
    ) as mappool_file:
        return json.load(mappool_file)
