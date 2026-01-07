from fabric.widgets.box import Box
from typing import TYPE_CHECKING

from utils.widget_utils import merge

if TYPE_CHECKING:
    from ...bar import StatusBar

from .button import SystemTrayButton
from .items import SystemTrayItems


class SystemTrayWidget(Box):
    def __init__(self, statusbar: "StatusBar"):
        self.confh = statusbar.confh

        super().__init__(
            name="statusbar-system-tray",
            orientation=self.confh.orientation,  # type: ignore
            h_expand=True,
            v_expand=True,
            v_align="center",
            h_align="center",
            all_visible=True,
        )

        self.config = self.confh.config_modules["systemtray"]

        if self.confh.is_vertical():
            self.config = merge(self.config, self.config["if-vertical"])

        if self.config["collapse"]["enabled"]:
            self.add(SystemTrayButton(self))
        else:
            self.add(SystemTrayItems(self))
