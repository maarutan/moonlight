from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._config_handler import ConfigHandlerCavalade


class CavaCfg:
    def __init__(
        self,
        cfg: "ConfigHandlerCavalade",
    ) -> None:
        self._cfg = cfg

    def general(self) -> dict:
        dflt = {
            "bars": 50,
            "sensitivity": 100,
            "framerate": 60,
            "lower_cutoff_freq": 50,
            "higher_cutoff_freq": 8000,
            "autosens": 1,
            "bar_width": 1,
            "bar_spacing": 0,
        }
        i = self._cfg._get_nested("general", default=dflt)
        if isinstance(i, dict):
            return i
        return dflt

    def output(self) -> dict:
        dflt = {
            "method": "raw",
            "raw_target": "/tmp/cava.fifo",
            "bit_format": "16bit",
            "channels": "stereo",
        }
        i = self._cfg._get_nested("output", default=dflt)
        if isinstance(i, dict):
            return i
        return dflt

    def smoothing(self) -> dict:
        dflt = {
            "gravity": 200,
            "integral": 70,
            "ignore": 0,
            "monstercat": 1,
        }
        i = self._cfg._get_nested("smoothing", default=dflt)
        if isinstance(i, dict):
            return i
        return dflt

    def equalizer(self) -> dict:
        dflt = {
            "1": 1.00,
            "2": 1.00,
            "3": 1.00,
            "4": 1.00,
            "5": 1.00,
            "6": 1.00,
            "7": 1.00,
            "8": 1.00,
            "9": 1.00,
        }
        i = self._cfg._get_nested("eq", default=dflt)
        if isinstance(i, dict):
            return i
        return dflt
