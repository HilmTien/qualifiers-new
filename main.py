import sys

from dotenv import load_dotenv

from scripts import get_qualifier_lobbies
from utils import get_api


def sandbox(api) -> None:
    from qualifiers.tournament import Tournament

    t = Tournament(api, [112310075, 112307988], use_username=False)

    # print(t.results)

    print(t.get_scores_for_seed(3, [1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2]))


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
