from typing import Literal, Optional, TYPE_CHECKING
import gi


gi.require_version("Gtk", "3.0")

from fabric.widgets.box import Box
from .components.disk import Disk
from .components.ram import Ram
from .components.cpu import Cpu

if TYPE_CHECKING:
    from ...bar import StatusBar


class SystemMonitorWidget(Box):
    def __init__(
        self,
        statusbar: "StatusBar",
    ):
        self.confh = statusbar.confh
        super().__init__(
            name="statusbar-systemmonitor",
            orientation=self.confh.orientation,  # type: ignore
        )
        self.disk = Disk()
        self.ram = Ram()
        self.cpu = Cpu()

        config = self.confh.config_modules["systemmonitor"]

        if config["positions"] is None:
            positions = ["cpu", "ram", "disk"]

        for pos in config["positions"]:
            match pos:
                case "cpu":
                    self.add(self.cpu)
                case "ram":
                    self.add(self.ram)
                case "disk":
                    self.add(self.disk)
                case _:
                    pass
