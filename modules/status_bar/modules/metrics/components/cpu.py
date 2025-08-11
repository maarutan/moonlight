import psutil
from gi.repository import GLib  # type: ignore
from fabric.widgets.box import Box
from fabric.widgets.stack import Stack
from fabric.widgets.label import Label
from fabric.widgets.circularprogressbar import CircularProgressBar
from fabric.widgets.revealer import Revealer


class Cpu(Box):
    def __init__(self):
        super().__init__(
            orientation="h",
            spacing=4,
            h_expand=True,
            v_expand=True,
            v_align="center",
            h_align="center",
            name="cpu-widget",
            children=[],
        )

        self.icon_label = Label(markup="", name="cpu-icon")

        self.cpu_circle = CircularProgressBar(
            value=0.0,
            size=32,
            line_width=4,
            start_angle=150,
            end_angle=390,
            name="cpu-circle",
            child=self.icon_label,
        )

        self.percent_label = Label(label="0%", name="cpu-percent")

        self.revealer = Revealer(
            child=self.percent_label,
            transition_type="slide-left",
            transition_duration=200,
            child_revealed=False,
        )

        cpu_box = Box(
            spacing=4, orientation="h", children=[self.cpu_circle, self.revealer]
        )
        psutil.cpu_percent(interval=None)

        self.children = Stack(children=cpu_box)

        GLib.timeout_add(100, self._update_cpu)

    def _update_cpu(self):
        percent = psutil.cpu_percent(interval=None)
        frac = percent / 100.0

        self.cpu_circle.set_value(frac)

        self.percent_label.set_label(f"{int(percent)}%")

        if percent >= 90:
            self.icon_label.add_style_class("alert")
            self.cpu_circle.add_style_class("alert")
        else:
            self.icon_label.remove_style_class("alert")
            self.cpu_circle.remove_style_class("alert")

        return True
