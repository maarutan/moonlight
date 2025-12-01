from fabric.widgets.datetime import DateTime
from fabric.widgets.box import Box
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bar import StatusBar


class ClockWidget(Box):
    def __init__(self, init_class: "StatusBar"):
        self.conf = init_class

        super().__init__(
            name="sb_time",
            v_expand=True,
            h_expand=True,
            v_align="center",
            h_align="center",
            orientation="h" if self.conf.is_horizontal() else "v",
        )

        config = (
            self.conf.confh.get_option(f"{self.conf.widget_name}.widgets.time") or {}
        )

        self.conf_format = config.get("format", "")
        self.conf_if_vertical = config.get("if-vertical", {})

        if self.conf.is_horizontal():
            final_format = self.conf_format
        else:
            final_format = self.conf_if_vertical.get("format", self.conf_format)

        self.add(
            DateTime(
                name="sb_time",
                formatters=final_format,
            )
        )
