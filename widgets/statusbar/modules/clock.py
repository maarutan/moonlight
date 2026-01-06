from fabric.widgets.datetime import DateTime
from fabric.widgets.box import Box
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bar import StatusBar


class ClockWidget(Box):
    def __init__(
        self,
        statusbar: "StatusBar",
    ):
        self.confh = statusbar.confh
        config = self.confh.config_modules["clock"]

        super().__init__(
            v_expand=True,
            h_expand=True,
            v_align="center",
            h_align="center",
            orientation=self.confh.orientation,  # type: ignore
        )

        self.conf_format = config["format"]

        self.conf_format = config["format"]

        if self.confh.is_vertical():
            final_format = config["if-vertical"]["format"] or self.conf_format
        else:
            final_format = self.conf_format

        datetime = DateTime(
            name="statusbar-clock",
            formatters=final_format,
        )

        if self.confh.is_vertical():
            datetime.add_style_class("statusbar-clock-vertical")

        self.add(datetime)
