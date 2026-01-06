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

        config = self.confh.config_modules["systemtray"]

        if self.confh.is_vertical():
            config = merge(config, config["if-vertical"])

        conf_collapse = config["collapse"]
        conf_collapse_enabled = conf_collapse["enabled"]
        conf_collapse_button_size = conf_collapse["button-size"]
        conf_collapse_columns = conf_collapse["columns"]
        conf_size = config["icon-size"]

        if conf_collapse_enabled:
            self.add(
                SystemTrayButton(
                    statusbar_config=self.confh,
                    columns=conf_collapse_columns,
                    icon_size=conf_size,
                    button_size=conf_collapse_button_size,
                )
            )
        else:
            self.add(
                SystemTrayItems(
                    statusbar_config=self.confh,
                    icon_size=conf_size,
                )
            )
