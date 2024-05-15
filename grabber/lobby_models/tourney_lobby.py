from dataclasses import dataclass

from ossapi.ossapi import MatchInfo

from custom_types import Scoring


@dataclass
class TournamentLobby:
    lobby_info: MatchInfo


@dataclass
class PartialLobby(TournamentLobby):
    faults: Scoring


@dataclass
class CompleteLobby(TournamentLobby):
    pass
