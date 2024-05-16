from ossapi import OssapiV1

from qualifiers.tournament import Tournament
from settings import COMPLETED_FILE, PARTIALS_FILE, get_data


def get_results(api: OssapiV1):
    mp_ids = get_data(COMPLETED_FILE) + get_data(PARTIALS_FILE)

    t = Tournament(api, mp_ids)

    print(t.results)
    print(
        t.get_scores_for_seed(
            1,
            {
                "NM1": 3,
                "NM2": 1,
                "NM3": 2,
                "HD1": 1,
                "HR1": 7,
                "DT1": 5,
                "FrM1": 6,
                "HDHR1": 6,
            },
        )
    )
    t.save_results()
