from typing import TYPE_CHECKING
from fabric.widgets.box import Box
from services.audio_status_provider import AudioStatusProvider

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
        self.provider.changed.connect(self.on_audio_changed)
        self.provider.micro_changed.connect(self.on_micro_changed)

    def on_audio_changed(self):
        print()
        print("Audio type changed ->", self.provider.status)

    def on_micro_changed(self):
        print("Microphone type changed ->", self.provider.micro)
        print()
