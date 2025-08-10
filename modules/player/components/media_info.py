from fabric.widgets.label import Label
import gi

from typing import Optional
from loguru import logger

from fabric.widgets.box import Box
from gi.repository import Gtk  # type:ignore

gi.require_version("Gdk", "3.0")


class PlayerMediaInfo(Box):
    def __init__(
        self,
        player_icon: str = "",
        player: str = "Unknown",
        title: str = "Nothing Playing",
        artist: str = "¯\\_(ツ)_/¯",
        album: str = "Enjoy the silence",
    ):
        self.player_icon = player_icon
        self.player = player
        self.title = title
        self.artist = artist
        self.album = album

        super().__init__(
            name="preview_image",
            orientation=Gtk.Orientation.VERTICAL,
            h_align="fill",
            v_align="fill",
            children=self._make_media_info(),
        )

    def _make_media_info(self):
        return Box(
            name="player-popup-current-select",
            orientation=Gtk.Orientation.VERTICAL,
            spacing=2,
            h_align="start",
            children=[
                Box(
                    name="player-popup-current-select-icon",
                    children=[
                        Label(name="player-popup-player-name", label=f"player:"),
                        Label(
                            name="player-popup-current-select",
                            label=f" {self.player_icon} {self.player}",
                        ),
                    ],
                ),
                Box(
                    name="player-popup-current-artist",
                    children=[
                        Label(name="player-popup-player-name", label=f"artist:"),
                        Label(
                            name="player-popup-current-select",
                            label=f" {self.artist}",
                        ),
                    ],
                ),
                Box(
                    name="player-popup-current-artist",
                    children=[
                        Label(name="player-popup-player-name", label=f"title:"),
                        Label(
                            name="player-popup-current-select-title",
                            label=f" {self.title}",
                        ),
                    ],
                ),
            ],
        )
