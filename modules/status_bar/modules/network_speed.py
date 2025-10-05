from typing import Literal
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from gi.repository import GLib  # type: ignore
from utils import setup_cursor_hover

from services import NetworkSpeed as network_speed

SpeedType = Literal["download", "upload", "all"]
IconPos = Literal["left", "right"]


class NetworkSpeed(Box):
    def __init__(
        self,
        is_horizontal: bool = True,
        speed_type: SpeedType = "download",
        icon_position: IconPos = "left",
        icon_download: str = "󰇚",
        icon_upload: str = "󰕒",
        if_one_icon: str = "",
        interval: int = 1,
    ):
        super().__init__(
            name="status-bar-network-speed", h_align="center", v_align="center"
        )

        self.is_horizontal = is_horizontal
        self.speed_type = speed_type
        self.icon_position = icon_position
        self.icon_download = icon_download
        self.icon_upload = icon_upload
        self.if_one_icon = if_one_icon

        self.speed_label = Label(name="status-bar-network-speed-label")
        self.icon_label = Label(
            name="status-bar-network-speed-icon", label=self.if_one_icon
        )

        self.main_box = Box(
            name="status-bar-network-speed-main-box",
            orientation="h" if is_horizontal else "v",
            h_align="center",
            v_align="center",
        )

        self.btn = Button(
            name="status-bar-network-speed-btn", h_align="center", v_align="center"
        )
        setup_cursor_hover(self.btn)
        self.btn.add(self.main_box)
        self.btn.connect("clicked", self.toggle_mode)
        self.add(self.btn)

        self.update_ui()
        GLib.timeout_add_seconds(interval, self.refresh)
        self.show_all()

    def refresh(self):
        self.update_ui()
        return True

    def _normalize_text(self, text: str) -> str:
        num, unit = text.split()
        unit = unit.replace("/s", "")
        lines = []
        for i in range(0, len(num), 2):
            lines.append(num[i : i + 2])
        lines.append(unit)
        return "\n".join(lines)

    def update_ui(self):
        data = network_speed().get_network_speed()

        if self.speed_type == "download":
            text = (
                f"{data['download']}"
                if self.is_horizontal
                else self._normalize_text(data["download"])
            )
            icon = self.icon_download

        elif self.speed_type == "upload":
            text = (
                f"{data['upload']}"
                if self.is_horizontal
                else self._normalize_text(data["upload"])
            )
            icon = self.icon_upload

        else:  # all
            if self.is_horizontal:
                text = (
                    f"↓ {data['download']} | ↑ {data['upload']}"
                    if self.icon_position == "left"
                    else f"{data['download']} ↓ | {data['upload']} ↑"
                )
            else:
                text = (
                    f"↓\n{self._normalize_text(data['download'])}\n↑\n{self._normalize_text(data['upload'])}"
                    if self.icon_position == "left"
                    else f"{self._normalize_text(data['download'])}\n↓\n{self._normalize_text(data['upload'])}\n↑"
                )
            icon = ""

        self.speed_label.set_text(text)
        self.icon_label.set_text(icon)

        # очищаем и добавляем заново в зависимости от позиции
        for child in self.main_box.get_children():
            self.main_box.remove(child)

        if self.icon_position == "left":
            self.main_box.add(self.icon_label)
            self.main_box.add(self.speed_label)
        else:
            self.main_box.add(self.speed_label)
            self.main_box.add(self.icon_label)

        self.main_box.show_all()
        return False

    def toggle_mode(self, *_):
        if self.speed_type == "all":
            self.speed_type = self.last_single_type
        else:
            self.last_single_type = self.speed_type
            self.speed_type = "all"
        self.update_ui()
