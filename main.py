import os
import sys
from datetime import timedelta

import ossapi
from dotenv import load_dotenv

from scripts import get_qualifier_lobbies
from utils import get_absolute_path


def main() -> None:
    load_dotenv()

    assert len(sys.argv) > 1, "CLI arguments must be passed."

    osu_api_v1_key = os.environ.get("OSU_API_V1_KEY")
    if osu_api_v1_key is None:
        raise NameError("OSU_API_V1_KEY not found in .env!")

    api = ossapi.OssapiV1(osu_api_v1_key)

    match sys.argv[1]:
        case "get":
            assert (
                7 <= len(sys.argv) <= 9
            ), "wrong amounts of arguments to 'get', check get_qualifier_lobbies signature"
            try:
                sys.argv[7] = timedelta(minutes=sys.argv[7])
                sys.argv[8] = timedelta(minutes=sys.argv[8])
            except IndexError:
                pass
            get_qualifier_lobbies(api, *sys.argv[2:])


if __name__ == "__main__":
    main()
