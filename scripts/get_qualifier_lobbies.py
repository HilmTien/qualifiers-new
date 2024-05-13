import json
import os
from datetime import UTC, datetime, timedelta

from ossapi import OssapiV1

from grabber import Grabber
from utils import get_data_folder


def get_qualifier_lobbies(
    api: OssapiV1,
    tourney_data_name: str,
    schedule_filename: str,
    acronym: str,
    save_filename: str,
    failed_filename: str,
    log_filename: str,
    time_before: timedelta = timedelta(minutes=10),
    max_time_after: timedelta = timedelta(minutes=10),
):
    log = []

    data_folder = get_data_folder(tourney_data_name)

    with open(os.path.join(data_folder, schedule_filename)) as schedule_file:
        schedule = json.load(schedule_file)

    failed = []
    passed = []

    grabber = Grabber(api, acronym)

    for time_raw in schedule:
        time = datetime.fromisoformat(time_raw).replace(tzinfo=UTC)

        initial_id = grabber.find_id(time - time_before)

        try:
            found_id = grabber.find_lobby(time, initial_id, max_time_after)
            if found_id == -1:
                log.append(f"aborted {time}")
                failed.append(time_raw)
                continue
            log.append(f"found {time}! {found_id}")
            passed.append(found_id)
        except LookupError:
            log.append(f"did not find lobby for {time}")
            failed.append(time_raw)
            continue

    with open(os.path.join(data_folder, log_filename), "w") as log_file:
        log_file.write("\n".join(log))

    save_path = os.path.join(data_folder, save_filename)

    try:
        with open(save_path) as savefile:
            existing_ids: list = json.load(savefile)
            existing_ids.extend(passed)

        with open(save_path, "w") as savefile:
            json.dump(list(set(existing_ids)), savefile)

    except FileNotFoundError:
        with open(save_path, "x") as savefile:
            json.dump(passed, savefile)

    with open(os.path.join(data_folder, failed_filename), "w") as failed_file:
        json.dump(failed, failed_file)
