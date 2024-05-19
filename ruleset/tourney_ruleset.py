from dataclasses import dataclass

from .gamemode import GameMode


@dataclass
class Ruleset:
    gamemode: GameMode
    teams: bool
    required_runs: int
    runs: int
    must_be_complete: bool
