from utils import JsonManager, FileManager
from config import DOCK_STATION_PINS


class PinsCfg:
    def __init__(self):
        self.json = JsonManager()
        self.fm = FileManager()

        DEFULT_PINS = {
            "pinned": [],
        }

        if not DOCK_STATION_PINS.exists():
            self.json.write(DOCK_STATION_PINS, DEFULT_PINS)
            self.fm.if_not_exists_create(DOCK_STATION_PINS)
