from typing import Optional
from fabric.widgets.box import Box
from fabric.widgets.wayland import WaylandWindow as Window
import gi

from .components.preview_image import PlayerPreviewImage
from .components.media_info import PlayerMediaInfo
from .components.progress_bar import PlayerProgressBar

gi.require_version("Gdk", "3.0")
from gi.repository import Gtk  # type:ignore


class PlyaerWidget(Box):
    def __init__(
        self,
        player_preview_image: Optional[str] = None,
        player_icon: str = "",
        player: str = "Unknown",
        title: str = "Nothing Playing",
        artist: str = "¯\\_(ツ)_/¯",
        album: str = "Enjoy the silence",
        media_value_length: tuple[
            float | int,
            float | int,
        ] = (
            0,
            1,
        ),  # 0 - min ;  1 - max
    ):
        self.player = player
        self.title = title
        self.artist = artist
        self.album = album
        self.media_value_length = media_value_length

        super().__init__(
            name="player",
            orientation=Gtk.Orientation.VERTICAL,
            h_align="fill",
            v_align="fill",
            visible=True,
            all_visible=True,
            children=[
                PlayerPreviewImage(
                    player_image_preview_path=player_preview_image,
                ),
                PlayerMediaInfo(
                    player_icon=player_icon,
                    player=self.player,
                    title=self.title,
                    artist=self.artist,
                    album=self.album,
                ),
                PlayerProgressBar(
                    media_value_length=self.media_value_length,
                ),
            ],
        )


class PlayerWrapper(Window):
    def __init__(self):
        super().__init__(
            name="player-wrapper", anchor="top right", layer="top", child=PlyaerWidget()
        )
