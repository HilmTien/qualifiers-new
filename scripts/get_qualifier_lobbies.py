import json
from datetime import UTC, datetime

from ossapi import OssapiV1

from grabber import Grabber
from grabber.lobby_models import CompleteLobby, PartialLobby
from settings import (
    ACRONYM,
    COMPLETED_FILE,
    FAILED_FILE,
    LOG_FILE,
    MAX_TIME_AFTER_SCHEDULE,
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

    grabber = Grabber(api, ACRONYM, logger=log)

    for time_raw in schedule:
        print(f"processing {time_raw}")
        log.append(f"processing {time_raw}")

        time = datetime.fromisoformat(time_raw).replace(tzinfo=UTC)

        # initial_id = grabber.find_id(time - TIME_BEFORE_SCHEDULE)
        initial_id = 113899618

        try:
            found = grabber.find_lobby(time, initial_id, MAX_TIME_AFTER_SCHEDULE)
            log.append(f"found {time}! {found}")
            match found:
                case CompleteLobby():
                    log.append(f"lobby is complete")
                    passed.append(found.lobby_info.match.match_id)
                case PartialLobby():
                    log.append(f"lobby is incomplete!")
                    log.append(str(found.faults))
                    partials.append(found.lobby_info.match.match_id)
        except KeyboardInterrupt:
            log.append(f"aborted {time}")
            failed.append(time_raw)
            continue
        except LookupError:
            log.append(f"did not find lobby for {time}")
            failed.append(time_raw)
            continue

    with open(get_path(LOG_FILE), "w", encoding="utf-8") as log_file:
        log_file.write("\n".join(log))

    save_lobbies(passed, get_path(COMPLETED_FILE))
    save_lobbies(partials, get_path(PARTIALS_FILE))

    with open(get_path(FAILED_FILE), "w") as failed_file:
        json.dump(failed, failed_file)
