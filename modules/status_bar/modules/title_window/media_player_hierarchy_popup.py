# player_hierarchy_popup.py

from os import name

from fabric.widgets.box import Box
from utils.json_manager import JsonManager
from .components_media_player.player import _make_selected_player_view
from .components_media_player.hierarchy import _make_hierarchy

from loguru import logger
from utils import WINDOW_TITLE_MAP
from services import PlayerManager

from fabric.widgets.wayland import WaylandWindow as Window
from fabric.utils import GLib  # type: ignore
from fabric.widgets.centerbox import CenterBox
from utils import GetPreviewPath
from config import STATUS_BAR_LOCK_MODULES


class PlayerHierarchyPopup(Window):
    def __init__(self):
        super().__init__(
            name="player-hierarchy-popup",
            anchor="top center",
            title="Player Hierarchy",
            exclusivity="none",
            layer="top",
            h_align="fill",
            v_align="fill",
        )
        self.selected_player_id = ""
        self.art_url_base = []
        self.json = JsonManager()
        self.status_bar_lock_modules = STATUS_BAR_LOCK_MODULES

        self.players = PlayerManager()
        self._is_paused = True if self.players.is_playing() else False

        self.merged_titles = WINDOW_TITLE_MAP
        self.preview_resolver = GetPreviewPath()
        self._last_hidden_box = None
        self._box_by_pid = {}
        self.on_player_changed = None

        GLib.timeout_add_seconds(2.5, self._refresh_all)

    def _refresh_all(self):
        self.children = CenterBox(
            start_children=[_make_selected_player_view(self)],
            center_children=[Box(name="vertical-line", orientation="v")],
            end_children=[_make_hierarchy(self)],
        )
        return True

    def _set_selected_player(self, pid: str):
        print(">>> set_selected_player called with pid:", pid)
        self.selected_player_id = pid
        box = self._box_by_pid.get(pid)
        if box:
            if self._last_hidden_box and self._last_hidden_box is not box:
                self._last_hidden_box.set_visible(True)
            box.set_visible(False)
            self._last_hidden_box = box
        if self.on_player_changed:
            print(">>> calling on_player_changed")
            self.on_player_changed(pid)

        return True
