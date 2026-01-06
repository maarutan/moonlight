import psutil
from gi.repository import GLib  # type: ignore
from fabric.widgets.box import Box
from fabric.widgets.stack import Stack
from fabric.widgets.label import Label
from fabric.widgets.circularprogressbar import CircularProgressBar
from fabric.widgets.revealer import Revealer


class Disk(Box):
    def __init__(self, path="/"):
        super().__init__(
            h_expand=True,
            v_expand=True,
            v_align="center",
            h_align="center",
            orientation="h",
            spacing=4,
            name="disk-widget",
            children=[],
        )

        self.path = path
        self.icon_label = Label(markup="󰋊", name="disk-icon")

        self.disk_circle = CircularProgressBar(
            value=0.0,
            size=32,
            line_width=4,
            start_angle=150,
            end_angle=390,
            name="disk-circle",
            child=self.icon_label,
        )

        self.percent_label = Label(label="0%", name="disk-percent")

        self.revealer = Revealer(
            child=self.percent_label,
            transition_type="slide-left",
            transition_duration=200,
            child_revealed=False,
        )

        disk_box = Box(
            spacing=4, orientation="h", children=[self.disk_circle, self.revealer]
        )
        self.children = Stack(children=disk_box)

        GLib.timeout_add(10000, self._update_disk)  # Обновляем раз в 10 секунд

    def _update_disk(self):
        usage = psutil.disk_usage(self.path)
        percent = usage.percent
        frac = percent / 100.0

        self.disk_circle.set_value(frac)

        used_gb = usage.used / (1024**3)
        total_gb = usage.total / (1024**3)
        self.percent_label.set_label(
            f"{int(percent)}% ({used_gb:.1f}/{total_gb:.1f} GB)"
        )

        if percent >= 90:
            self.icon_label.add_style_class("alert")
            self.disk_circle.add_style_class("alert")
        else:
            self.icon_label.remove_style_class("alert")
            self.disk_circle.remove_style_class("alert")

        return True
