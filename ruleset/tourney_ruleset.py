from dataclasses import dataclass


@dataclass
class Ruleset:
    teams: bool
    required_runs: int
    runs: int
