from typing import Literal, Optional
import gi

gi.require_version("Gtk", "3.0")

from fabric.widgets.box import Box
from fabric.widgets.centerbox import CenterBox

from .components.disk import Disk
from .components.ram import Ram
from .components.cpu import Cpu


class Metrics(Box):
    def __init__(
        self,
        is_horizontal=True,
        positions: Optional[list[str]] = None,
    ):
        super().__init__(
            orientation="h" if is_horizontal else "v",
        )
        self.disk = Disk()
        self.ram = Ram()
        self.cpu = Cpu()

        if positions is None:
            positions = ["cpu", "ram", "disk"]

        for pos in positions:
            match pos:
                case "cpu":
                    self.add(self.cpu)
                case "ram":
                    self.add(self.ram)
                case "disk":
                    self.add(self.disk)
                case _:
                    pass
