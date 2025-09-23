from __future__ import annotations

import re
from typing import Literal
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib  # type: ignore


from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.button import Button

from services.networkspeed import NetworkSpeed as network_speed


SpeedType = Literal["download", "upload", "all"]
SpeedUnit = Literal["b", "kb", "mb", "gb"]
IconPos = Literal["left", "right"]


class NetworkSpeedWidget(Box):
    _UNIT_MAP = {
        "b": 1.0,
        "kb": 1024.0,
        "mb": 1024.0 * 1024.0,
        "gb": 1024.0 * 1024.0 * 1024.0,
    }

    _STR_UNIT_TO_BYTES = {
        "B/S": 1.0,
        "BPS": 1.0,
        "KB/S": 1024.0,
        "KPS": 1024.0,
        "MB/S": 1024.0 * 1024.0,
        "MPS": 1024.0 * 1024.0,
        "GB/S": 1024.0 * 1024.0 * 1024.0,
        "GPS": 1024.0 * 1024.0 * 1024.0,
    }

    def __init__(
        self,
        is_horizontal: bool = True,
        speed_type: str = "download",
        icon_position: str = "left",
        icon_download: str = "󰇚",
        icon_upload: str = "󰕒",
        icon_all: str = "",
        speed_unit: str = "kb",
        interval: int = 1,
    ):
        super().__init__(
            name="status-bar-network-speed",
            orientation="h" if is_horizontal else "v",
            h_align="center",
            v_align="center",
            spacing=4,
        )

        self.speed_type: SpeedType = speed_type
        self.icon_position: IconPos = icon_position
        self.icon_download = icon_download
        self.icon_upload = icon_upload
        self.icon_all = icon_all
        self.speed_unit: SpeedUnit = speed_unit
        self.interval_sec: int = max(1, int(interval))

        self.speed_service = network_speed()

        # Иконки
        self._icon_dl = Label(name="net-speed-icon-download", label=self.icon_download)
        self._icon_ul = Label(name="net-speed-icon-upload", label=self.icon_upload)
        self._icon_one = Label(name="net-speed-icon-one", label=self.icon_all)

        # Подписи
        self._label_one = Label(name="net-speed-label-one", label="0.0 KB/s")
        self._label_dl = Label(name="net-speed-label-dl", label="0.0 KB/s")
        self._label_ul = Label(name="net-speed-label-ul", label="0.0 KB/s")

        # Внутренний контейнер
        self._main_box = Box(
            name="status-bar-network-speed-main-box",
            orientation="h" if is_horizontal else "v",
            h_align="center",
            v_align="center",
            spacing=4,
        )

        self._btn = Button(
            name="status-bar-network-speed-btn",
            h_align="center",
            v_align="center",
            child=self._main_box,
        )

        # Сборка интерфейса
        self._build_layout()
        self.add(self._btn)
        self.show_all()

        # Первое обновление и запуск таймера
        self._update_once()
        GLib.timeout_add_seconds(self.interval_sec, self._on_tick)

    def _build_layout(self):
        for child in list(self._main_box.get_children()):
            self._main_box.remove(child)

        if self.speed_type == "all":
            dl_box = Box(orientation="h", spacing=2)
            dl_box.pack_start(self._icon_dl, False, False, 0)
            dl_box.pack_start(self._label_dl, False, False, 0)

            ul_box = Box(orientation="h", spacing=2)
            ul_box.pack_start(self._icon_ul, False, False, 0)
            ul_box.pack_start(self._label_ul, False, False, 0)

            self._delimiter = Label(name="net-speed-delimiter", label="  |  ")
            self._main_box.pack_start(dl_box, False, False, 0)
            self._main_box.pack_start(self._delimiter, False, False, 0)
            self._main_box.pack_start(ul_box, False, False, 0)
        else:
            if self.icon_position == "left":
                self._main_box.pack_start(self._icon_one, False, False, 0)
                self._main_box.pack_start(self._label_one, False, False, 0)
            else:
                self._main_box.pack_start(self._label_one, False, False, 0)
                self._main_box.pack_start(self._icon_one, False, False, 0)

    def _on_tick(self) -> bool:
        self._update_once()
        return True

    def _update_once(self):
        data = self.speed_service.get_network_speed()
        if not data:
            return

        dl_bps = self._ensure_number_bps(data.get("download"))
        ul_bps = self._ensure_number_bps(data.get("upload"))

        dl_fmt = self._format_speed(dl_bps)
        ul_fmt = self._format_speed(ul_bps)

        if self.speed_type == "all":
            self._label_dl.set_text(dl_fmt)
            self._label_ul.set_text(ul_fmt)
        elif self.speed_type == "download":
            self._label_one.set_text(dl_fmt)
        else:  # upload
            self._label_one.set_text(ul_fmt)

    def _format_speed(self, bps: float) -> str:
        denom = self._UNIT_MAP[self.speed_unit]
        val = bps / denom
        if self.speed_unit in ("b", "kb"):
            return f"{val:.1f} {self.speed_unit.upper()}/s"
        return f"{val:.2f} {self.speed_unit.upper()}/s"

    def _ensure_number_bps(self, value) -> float:
        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            m = re.search(r"([0-9]*\.?[0-9]+)\s*([A-Za-z/]+)", value.strip())
            if m:
                num = float(m.group(1))
                unit_raw = m.group(2).upper().replace(" ", "")
                unit_norm = unit_raw
                if not unit_norm.endswith(("/S", "PS")):
                    unit_norm += "/S"

                factor = self._STR_UNIT_TO_BYTES.get(unit_norm, 1.0)
                return num * factor

        return 0.0


if __name__ == "__main__":
    win = Gtk.Window()
    widget = NetworkSpeedWidget(speed_type="all")
    win.add(widget)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
