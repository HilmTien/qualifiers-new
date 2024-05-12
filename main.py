import os

import ossapi
from dotenv import load_dotenv

from grabber import Grabber


def main() -> None:
    load_dotenv()

    osu_api_v1_key = os.environ.get("OSU_API_V1_KEY")
    if osu_api_v1_key is None:
        raise NameError("OSU_API_V1_KEY not found in .env!")

    api = ossapi.OssapiV1(osu_api_v1_key)

    print(api.get_match(113855673))
    # with Grabber(api) as grabber:
    #     grabber._get_latest_live_lobby()


if __name__ == "__main__":
    main()
