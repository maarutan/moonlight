from typing import Literal
from fabric.audio.service import Audio
from fabric.utils import cooldown
from fabric.widgets.eventbox import EventBox
from fabric.widgets.circularprogressbar import CircularProgressBar
from utils.icons import text_icons, symbolic_icons, text_icons
from fabric.widgets.label import Label
from fabric.widgets.overlay import Overlay


class VolumeControl(EventBox):
    def __init__(self, **kwargs):
        super().__init__(
            name="volume",
            events=["scroll", "smooth-scroll", "enter-notify-event"],
            **kwargs,
        )

        self.audio = Audio()

        self.progress_bar = CircularProgressBar(
            style_classes="overlay-progress-bar",
            pie=True,
            size=24,
        )

        self.icon = self.nerd_font_icon(
            icon=text_icons["volume"]["medium"],
            props={
                "style_classes": "panel-font-icon overlay-icon",
            },
        )

        self.box.add(
            Overlay(child=self.progress_bar, overlays=self.icon, name="overlay"),
        )

        self.audio.connect("notify::speaker", self.on_speaker_changed)

        self.connect("scroll-event", self.on_scroll)
        if self.config.get("label", True):
            self.volume_label = Label(style_classes="panel-text")
            self.box.add(self.volume_label)

    @cooldown(0.1)
    def on_scroll(self, _, event):
        # Adjust the volume based on the scroll direction
        val_y = event.delta_y

        if val_y > 0:
            self.audio.speaker.volume += self.config["step_size"]
        else:
            self.audio.speaker.volume -= self.config["step_size"]

    def nerd_font_icon(self, icon: str, props=None, name="nerd-icon") -> Label:
        label_props = {
            "label": str(icon),  # Directly use the provided icon name
            "name": name,
            "h_align": "center",  # Align horizontally
            "v_align": "center",  # Align vertically
        }

        if props:
            label_props.update(props)

        return Label(**label_props)

    def on_speaker_changed(self, *_):
        # Update the progress bar value based on the speaker volume
        if not self.audio.speaker:
            return

        if self.config.get("tooltip", False):
            self.set_tooltip_text(self.audio.speaker.description)

        self.audio.speaker.connect("notify::volume", self.update_volume)
        self.update_volume()

    # Mute and unmute the speaker
    def toggle_mute(self):
        current_stream = self.audio.speaker
        if current_stream:
            current_stream.muted = not current_stream.muted
            self.icon.set_text(
                text_icons["volume"]["muted"]
            ) if current_stream.muted else self.update_volume()

    def update_volume(self, *_):
        if self.audio.speaker:
            volume = round(self.audio.speaker.volume)
            self.progress_bar.set_value(volume / 100)

            if self.config.get("label", True):
                self.volume_label.set_text(f"{volume}%")

        self.icon.set_text(
            self.get_audio_icon_name(int(volume), self.audio.speaker.muted)["text_icon"]
        )

    def get_audio_icon_name(
        self, volume: int, is_muted: bool
    ) -> dict[Literal["icon_text", "icon"], str]:
        if volume <= 0 or is_muted:
            return {
                "text_icon": text_icons["volume"]["muted"],
                "icon": symbolic_icons["audio"]["volume"]["muted"],
            }
        if volume > 0 and volume <= 32:
            return {
                "text_icon": text_icons["volume"]["low"],
                "icon": symbolic_icons["audio"]["volume"]["low"],
            }
        if volume > 32 and volume <= 66:
            return {
                "text_icon": text_icons["volume"]["medium"],
                "icon": symbolic_icons["audio"]["volume"]["medium"],
            }
        if volume > 66 and volume <= 100:
            return {
                "text_icon": text_icons["volume"]["high"],
                "icon": symbolic_icons["audio"]["volume"]["high"],
            }
        else:
            return {
                "text_icon": text_icons["volume"]["overamplified"],
                "icon": symbolic_icons["audio"]["volume"]["overamplified"],
            }
