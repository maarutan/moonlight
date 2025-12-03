from fabric.widgets.box import Box
from typing import TYPE_CHECKING

from utils.widget_utils import merge

if TYPE_CHECKING:
    from ...bar import StatusBar

from .button import SystemTrayButton
from .items import SystemTrayItems


class SystemTrayWidget(Box):
    def __init__(self, class_init: "StatusBar"):
        self.conf = class_init
        is_horizontal = self.conf.is_horizontal()
        orientation = "h" if is_horizontal else "v"

        super().__init__(
            name="sb_system-tray",
            orientation=orientation,
            h_expand=True,
            v_expand=True,
            v_align="center",
            h_align="center",
            all_visible=True,
        )

        config = self.conf.confh.get_option(
            f"{self.conf.widget_name}.widgets.system-tray", {}
        )

        if not is_horizontal:
            config = merge(config, config.get("if-vertical", {}))

        conf_collapse = config.get("collapse", {})
        conf_collapse_enabled = conf_collapse.get("enabled", True)
        conf_collapse_button_size = conf_collapse.get("button-size", 24)
        conf_collapse_columns = conf_collapse.get("columns", 4)
        conf_size = config.get("icon-size", 24)

        if conf_collapse_enabled:
            self.add(
                SystemTrayButton(
                    class_init=self.conf,
                    columns=conf_collapse_columns,
                    icon_size=conf_size,
                    button_size=conf_collapse_button_size,
                )
            )
        else:
            self.add(
                SystemTrayItems(
                    class_init=self.conf,
                    icon_size=conf_size,
                )
            )
