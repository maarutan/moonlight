from typing import TYPE_CHECKING, Optional
from fabric.widgets.box import Box
from fabric.utils import idle_add
from fabric.widgets.button import Button
from fabric.widgets.svg import Svg
from services.audio_status_provider import AudioStatusProvider
from services.headset import HeadsetService
from fabric.audio.service import Audio
from utils.widget_utils import setup_cursor_hover
from .icon_handler import HeadphoneIoncs
from .status import HeadphoneStatus

if TYPE_CHECKING:
    from ...bar import StatusBar


class HeadphoneWidget(Box):
    def __init__(self, statusbar: "StatusBar"):
        super().__init__(
            name="statusbar-headphones",
            orientation="h",
            h_expand=True,
            v_expand=True,
            v_align="center",
            h_align="center",
        )
        self.statusbar = statusbar
        self.provider = AudioStatusProvider()
        self.audio = Audio()
        self.headset = HeadsetService()
        self.status_obj = HeadphoneStatus(self)
        self.icon_handler = HeadphoneIoncs(self)
        self.svg: Optional[Svg] = None
        idle_add(self._refresh)
        self.headset.changed.connect(lambda *a, **k: idle_add(self._refresh))
        self.provider.changed.connect(lambda *a, **k: idle_add(self._refresh))
        if hasattr(self.audio, "microphone_changed"):
            self.audio.microphone_changed.connect(
                lambda *a, **k: idle_add(self._refresh)
            )

    def _refresh(self):
        for child in list(self.get_children()):
            self.remove(child)

        if self.provider.status == "unknown":
            return

        self.status_obj.update()
        self.icon_handler.update()
        svg = Svg(
            name="statusbar-headphones-icon",
            size=self.statusbar.confh.config_modules["headphones"]["icon-size"],
            svg_string=self.icon_handler.icon or "",
        )
        self.svg = svg
        btn = Button(
            name="statusbar-headphones-button",
            child=svg,
            on_clicked=lambda *_: self.status_obj.send_notify(),
        )
        setup_cursor_hover(btn)
        btn.set_tooltip_text(f"{self.status_obj.name} - {self.status_obj.status}")
        self.add(btn)
