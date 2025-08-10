from typing import Literal
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib  # type: ignore

import psutil
from fabric.widgets.box import Box
from fabric.widgets.stack import Stack
from fabric.widgets.label import Label
from fabric.widgets.circularprogressbar import CircularProgressBar
from fabric.widgets.revealer import Revealer
from fabric.widgets.centerbox import CenterBox


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


class Metrics(Box):
    def __init__(
        self,
        is_horizontal=True,
    ):
        self.is_horizontal = is_horizontal
        self.disk = Disk()
        self.ram = Ram()
        self.cpu = Cpu()
        super().__init__(
            spacing=5,
            orientation="h" if self.is_horizontal else "v",
            children=CenterBox(
                orientation="h" if self.is_horizontal else "v",
                start_children=self.cpu,
                center_children=self.ram,
                end_children=self.disk,
            ),
        )
