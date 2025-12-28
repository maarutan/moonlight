from fabric.widgets.wayland import WaylandWindow as Window
from fabric.utils.helpers import invoke_repeater, idle_add
from fabric.widgets.label import Label
from fabric.widgets.svg import Svg
from fabric.widgets.box import Box
from time import strftime

from .config import DayInfoDesktopConfig

widget_name = "day-info-desktop"
confh = DayInfoDesktopConfig(widget_name)
enabled = confh.get_option(f"{widget_name}.enabled", True)

if not enabled:
    DayInfoDesktop = None  # pyright: ignore[reportAssignmentType]
else:

    class DayInfoDesktop(Window):
        def __init__(self):
            self.conf = confh
            config = self.conf.get_option(f"{widget_name}")

            self.conf_layer = config.get("layer", "")
            self.conf_anchor = config.get("anchor", "")
            self.conf_margin = config.get("margin", "")
            self.conf_weekday_enabled = config.get("weekday-enabled", True)
            self.conf_day_format = config.get("day-format", "")
            self.conf_time_format = config.get("time-format", "")
            self.conf_weekday_font_size = config.get("weekday-font-size", 32)
            self.conf_latter_spacing = config.get("latter-spacing", 10)

            super().__init__(
                name="day-info-window",
                margin=self.conf_margin,
                anchor=self.conf_anchor,
                layer=self.conf_layer,
                exclusivity="none",
                h_align="center",
                v_align="center",
                style="background:none;",
            )

            self.show_all()
            idle_add(self.update)
            invoke_repeater(1000, self.update)

        def update(self):
            box = Box(
                orientation="v",
            )

            weekday = self.weekday_label()
            day = self.day_label()
            time = self.time_label()

            box.children = [
                weekday,
                day,
                time,
            ]

            self.children = box
            return True

        def _what_day(self) -> str:
            return strftime("%A").lower()

        def weekday_label(self) -> Label:
            day = self._what_day().upper() if self.conf_weekday_enabled else ""
            label = Label(
                name="day-info-weekday", label=day, size=self.conf_weekday_font_size
            )
            label.set_style(f"""
                font-size: {self.conf_weekday_font_size}px;
                letter-spacing: {self.conf_latter_spacing}px;
            """)
            return label

        def day_label(self) -> Label:
            day_label = Label(
                name="day-info-day", label=strftime(self.conf_day_format).upper()
            )
            return day_label

        def time_label(self):
            time_label = Label(
                name="day-info-time",
                label=f"- {strftime(self.conf_time_format).upper()} -",
            )
            return time_label
