UserID = int
BeatmapID = int
Scoring = dict[UserID, dict[BeatmapID, int]]

JSON = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None
