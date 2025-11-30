from pathlib import Path

from test import Toster
from utils.constants import Const


def test_paths_exist():
    for name, val in Const.__dict__.items():
        if isinstance(val, Path):
            assert val.exists(), f"{name} not found: {val}"


if __name__ == "__main__":
    Toster(test_paths_exist)
