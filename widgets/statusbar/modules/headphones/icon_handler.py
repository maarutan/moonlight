from typing import TYPE_CHECKING
from fabric.widgets.svg import Svg
from .icons import icons

if TYPE_CHECKING:
    from .headphone_widget import HeadphoneWidget


class HeadphoneIoncs:
    def __init__(self, headphone: "HeadphoneWidget"):
        self.headphone = headphone
        self.percent = 0
        self.status = getattr(self.headphone.provider, "status", "unknown")
        initial_icons = icons(self.percent)
        self.icon = (
            initial_icons.get("headphone") or initial_icons.get("headphones") or ""
        )
        self.mic = None
        self._update_icon()

    def _update_icon(self):
        self.status = getattr(self.headphone.provider, "status", "unknown")
        try:
            percent_raw = self.headphone.headset.first_percentage() or 0
        except Exception:
            percent_raw = 0
        self.percent = int(percent_raw or 0)
        self.mic = getattr(self.headphone.audio, "microphone", None)
        mic_muted = (
            bool(getattr(self.mic, "muted", False)) if self.mic is not None else False
        )
        icons_for_percent = icons(self.percent)
        try:
            if mic_muted:
                if self.status == "bluetooth":
                    self.icon = (
                        icons_for_percent.get("bluetooth", {}).get("headphones")
                        or icons_for_percent.get("headphones")
                        or ""
                    )
                else:
                    self.icon = icons_for_percent.get("headphones") or ""
            else:
                if self.status == "bluetooth":
                    self.icon = (
                        icons_for_percent.get("bluetooth", {}).get(
                            "headphones_microphone"
                        )
                        or icons_for_percent.get("headphones_microphone")
                        or ""
                    )
                else:
                    self.icon = icons_for_percent.get("headphones_microphone") or ""
        except Exception:
            self.icon = (
                icons_for_percent.get("headphone")
                or icons_for_percent.get("headphones")
                or ""
            )

    def update(self):
        self._update_icon()
        if getattr(self.headphone, "svg", None) is not None:
            try:
                self.headphone.svg.set_from_string(self.icon or "")
            except Exception:
                pass
