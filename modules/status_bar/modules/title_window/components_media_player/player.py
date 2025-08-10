from os import name
from typing import TYPE_CHECKING
from config import PLACEHOLDER_IMAGE
from modules.player.player import PlyaerWidget
from services.player import MprisPlayer

if TYPE_CHECKING:
    from ..media_player_hierarchy_popup import PlayerHierarchyPopup

from loguru import logger
import re

from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.utils import Gdk, GdkPixbuf, Gtk, GLib  # type: ignore
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.eventbox import EventBox


def _make_media_player(self: "PlayerHierarchyPopup"):
    if self.players:
        media_value_length = (float(self.mp.position), float(self.mp.length))
        icon = next(
            (
                wt
                for wt in self.merged_titles
                if re.search(
                    wt[0],
                    self.selected_player_id
                    if self.selected_player_id
                    else self.mp.player_name,
                )
            ),
            (None, ""),
        )[1]
        return PlyaerWidget(
            player=self.selected_player_id,
            title=self.selected_title,
            artist=self.selected_artist,
            album=self.selected_album,
            media_value_length=media_value_length,
            player_preview_image=self.selected_preview_image,
            player_icon=icon,
        )
