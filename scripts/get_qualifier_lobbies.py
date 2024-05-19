import json
from datetime import UTC, datetime

from ossapi import OssapiV1

from grabber import Grabber
from grabber.lobby_models import CompleteLobby, OngoingLobby, PartialLobby
from settings import (
    ACRONYM,
    COMPLETED_FILE,
    FAILED_FILE,
    LOG_FILE,
    MAX_TIME_AFTER_SCHEDULE,
    PARTIAL_FAULTS_FILE,
    PARTIALS_FILE,
    SCHEDULE_FILE,
    TIME_BEFORE_SCHEDULE,
    get_data,
    get_path,
)
from utils import save_lobbies


def get_qualifier_lobbies(api: OssapiV1):
    log = []

    schedule = get_data(SCHEDULE_FILE)

    failed = []
    passed = []
    partials = []

    faults = []

    print(log)

    grabber = Grabber(api, logger=log)

    for time_raw, has_been_processed in schedule.items():
        print(f"processing {time_raw}")
        log.append(f"processing {time_raw}")

        if has_been_processed:
            print(f"{time_raw} has been processed already")
            log.append(f"{time_raw} has been processed already")
            continue

        time = datetime.fromisoformat(time_raw).replace(tzinfo=UTC)

        if time > datetime.now(tz=UTC):
            continue

        initial_id = grabber.find_id(time - TIME_BEFORE_SCHEDULE)

        try:
            found = grabber.find_lobby(time, initial_id)
            log.append(f"found {time}! {found}")
        except KeyboardInterrupt:
            log.append(f"aborted {time}")
            failed.append(time_raw)
            continue
        except LookupError:
            log.append(f"did not find lobby for {time}")
            failed.append(time_raw)
            continue

        match found:
            case CompleteLobby():
                log.append("lobby is complete")
                passed.append(found.lobby_info.match.match_id)
            case PartialLobby():
                log.append("lobby is incomplete!")
                log.append(str(found.faults))
                faults.extend(found.faults.keys())
                partials.append(found.lobby_info.match.match_id)
            case OngoingLobby():
                log.append("lobby is ongoing!")
                if found.is_complete:
                    log.append("lobby is complete, will be added to lobbies")
                    passed.append(found.lobby_info.match.match_id)
                else:
                    log.append("no way to deduce completeness, marking as failed")
                    failed.append(time_raw)

        schedule[time_raw] = True

    with open(get_path(LOG_FILE), "w", encoding="utf-8") as log_file:
        log_file.write("\n".join(log))

    save_lobbies(passed, get_path(COMPLETED_FILE))
    save_lobbies(partials, get_path(PARTIALS_FILE))

    save_lobbies(faults, get_path(PARTIAL_FAULTS_FILE))

    with open(get_path(FAILED_FILE), "w") as failed_file:
        json.dump(failed, failed_file)

    with open(get_path(SCHEDULE_FILE), "w") as schedule_file:
        json.dump(schedule, schedule_file)
