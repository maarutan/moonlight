import psutil
from gi.repository import GLib  # type: ignore
from fabric.widgets.box import Box
from fabric.widgets.stack import Stack
from fabric.widgets.label import Label
from fabric.widgets.circularprogressbar import CircularProgressBar
from fabric.widgets.revealer import Revealer


class Ram(Box):
    def __init__(self):
        super().__init__(
            orientation="h",
            h_expand=True,
            v_expand=True,
            v_align="center",
            h_align="center",
            spacing=4,
            name="ram-widget",
            children=[],
        )

        self.icon_label = Label(markup="", name="ram-icon")

        self.ram_circle = CircularProgressBar(
            value=0.0,
            size=32,
            line_width=4,
            start_angle=150,
            end_angle=390,
            name="ram-circle",
            child=self.icon_label,
        )

        self.percent_label = Label(label="0%", name="ram-percent")

        self.revealer = Revealer(
            child=self.percent_label,
            transition_type="slide-left",
            transition_duration=200,
            child_revealed=False,
        )

        ram_box = Box(
            spacing=4, orientation="h", children=[self.ram_circle, self.revealer]
        )

        self.children = Stack(children=ram_box)

        GLib.timeout_add(1000, self._update_ram)

    def _update_ram(self):
        mem = psutil.virtual_memory()
        percent = mem.percent
        frac = percent / 100.0

        self.ram_circle.set_value(frac)

        used_gb = mem.used / (1024**3)
        total_gb = mem.total / (1024**3)
        self.percent_label.set_label(
            f"{int(percent)}% ({used_gb:.1f}/{total_gb:.1f} GB)"
        )

        if percent >= 90:
            self.icon_label.add_style_class("alert")
            self.ram_circle.add_style_class("alert")
        else:
            self.icon_label.remove_style_class("alert")
            self.ram_circle.remove_style_class("alert")

        return True
