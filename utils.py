import json
import os
from datetime import UTC, datetime
from functools import cache
from typing import Literal

from ossapi import OssapiV1

from custom_types import BeatmapID


def get_absolute_path(file_path: str, *relative_path: str) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(file_path)), *relative_path)


def sign(value: int | float) -> Literal[-1, 1]:
    return -1 if value < 0 else 1


def save_lobbies(passed: list[BeatmapID], save_path: str):
    try:
        with open(save_path) as savefile:
            existing_ids: list = json.load(savefile)
            existing_ids.extend(passed)

        with open(save_path, "w") as savefile:
            json.dump(list(set(existing_ids)), savefile)

    except FileNotFoundError:
        with open(save_path, "x") as savefile:
            json.dump(passed, savefile)


@cache
def get_api() -> OssapiV1:
    osu_api_v1_key = os.environ.get("OSU_API_V1_KEY")
    if osu_api_v1_key is None:
        raise NameError("OSU_API_V1_KEY not found in .env!")

    return OssapiV1(osu_api_v1_key)


def make_schedule_json(datetimes: list[datetime], tournament_name: str):
    folder_path = get_absolute_path(__file__, "tournament_data", tournament_name)

    if not os.path.isdir(folder_path):
        os.mkdir(folder_path)

    schedule_data = [datetime.replace(tzinfo=UTC).isoformat() for datetime in datetimes]

    with open(os.path.join(folder_path, "schedule.json"), "w") as schedule_file:
        json.dump(schedule_data, schedule_file)


def main() -> None:
    # TTF
    # fri_hours = [10, 12, 13, 14, 15, 16, 17, 18, 20, 22]
    # sat_hours = [0, 2, 4, 6, 8, 10, 12, 13, 14, 15, 16, 17, 18, 20, 22]
    # sun_hours = [0, 2, 4, 6, 8, 10, 12]

    # fri_hours = [17, 16, 15, 14, 11, 9, 5, 4]
    sat_hours = [17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 6]
    # sun_hours = [14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 2]
    datetimes = []
    # datetimes += [datetime(2024, 5, 10, hour, tzinfo=UTC) for hour in fri_hours]
    datetimes += [datetime(2024, 5, 11, hour, tzinfo=UTC) for hour in sat_hours]
    # datetimes += [datetime(2024, 5, 12, hour, tzinfo=UTC) for hour in sun_hours]

    make_schedule_json(datetimes, "prism-2024")


if __name__ == "__main__":
    main()
