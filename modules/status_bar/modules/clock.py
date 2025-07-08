import time
from fabric.utils import GLib  # type: ignore
from fabric.widgets.box import Box
from fabric.widgets.button import Button
from fabric.widgets.datetime import DateTime
from fabric.widgets.label import Label
from gi.repository import Gtk, Gdk  # type: ignore


class Clock(Box):
    def __init__(
        self,
        format: int = 242,  # 12-hour format with AM/PM
        orientation_pos: bool = True,
    ):
        self.format = format
        self._orientation = orientation_pos

        if self.format == 12:
            time_format_horizontal = "%I:%M %p"
            time_format_vertical = "%I\n%M\n%p"
        elif self.format == 24:
            time_format_horizontal = "%H:%M"
            time_format_vertical = "%H\n%M"
        else:
            time_format_horizontal = "%H:%M:%S"
            time_format_vertical = "%H\n%M\n%S"

        self.date_time = DateTime(
            name="date-time",
            formatters=[time_format_horizontal]
            if self._orientation
            else [time_format_vertical],
            h_align="center" if self._orientation else "fill",
            v_align="center",
            h_expand=True,
            v_expand=True,
            style_classes=["vertical"] if not self._orientation else [],
        )
        super().__init__(
            name="clock",
            orientation="h" if self._orientation else "v",
            children=self.date_time,
        )
