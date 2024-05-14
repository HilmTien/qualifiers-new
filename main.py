import sys

from dotenv import load_dotenv

from scripts import get_qualifier_lobbies
from utils import get_api


def sandbox(api) -> None:
    from grabber import Grabber

    grabber = Grabber(api)

    print(grabber.lobby_is_complete(api.get_match(113855673)))


def main() -> None:
    load_dotenv()

    api = get_api()

    assert (
        len(sys.argv) == 2
    ), "Entry point not given. Look for scripts in Pipfile and run using 'pipenv run ---', for example 'pipenv run get'"

    match sys.argv[1]:
        case "get":
            get_qualifier_lobbies(api)
        case "sandbox":
            sandbox(api)


if __name__ == "__main__":
    main()
