import os
from typing import Literal


def get_absolute_path(file_path: str, relative_path: str) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(file_path)), relative_path)


def sign(value: int | float) -> Literal[-1, 1]:
    return -1 if value < 0 else 1
