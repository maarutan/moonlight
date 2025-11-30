import test_constants

from test import Toster

test_items = [
    test_constants.test_paths_exist,
]

for items in test_items:
    Toster(items)
