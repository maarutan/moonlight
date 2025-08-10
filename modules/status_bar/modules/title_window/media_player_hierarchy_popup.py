# player_hierarchy_popup.py


from fabric.widgets.box import Box
from utils.json_manager import JsonManager
from .components_media_player.player import _make_media_player
from .components_media_player.hierarchy import _make_hierarchy_for_select

from loguru import logger
from utils import WINDOW_TITLE_MAP
from services import MprisPlayerManager, MprisPlayer

from fabric.widgets.wayland import WaylandWindow as Window
from fabric.utils import GLib  # type: ignore
from fabric.widgets.centerbox import CenterBox
from utils import GetPreviewPath
from config import STATUS_BAR_LOCK_MODULES


class PlayerHierarchyPopup(Window):
    def __init__(
        self,
        background_path: str,
        # mpris_player: MprisPlayer,
        active_players: dict = {},
        ghost_size: int = 200,
        single_active_player: bool = True,
        if_empty_ghost_will_come_out: bool = True,
    ):
        super().__init__(
            name="player-hierarchy-popup",
            anchor="top center",
            title="Player Hierarchy",
            exclusivity="none",
            layer="top",
            h_align="fill",
            v_align="fill",
        )

        self.mpris_manager = MprisPlayerManager()  # <- вот сюда
        self.players = self.mpris_manager.players  # теперь можно брать
        self.active_players = active_players
        # print(active_players)

        for p in self.players:  # type: ignore
            self.mp = MprisPlayer(p)
        # self.mp = mpris_player

        self.selected_player_id = self.mp.player_name
        self.selected_title = self.mp.title
        self.selected_artist = self.mp.artist
        self.selected_album = self.mp.album
        self.selected_preview_image = self.mp.arturl

        self.ghost_size = ghost_size
        self.single_active_player = single_active_player
        self.if_empty_ghost_will_come_out = if_empty_ghost_will_come_out
        self.background_path = background_path

        self.art_url_base = []
        self.json = JsonManager()
        self.status_bar_lock_modules = STATUS_BAR_LOCK_MODULES

        self.mpris_manager = MprisPlayerManager()

        # self._is_paused = True if self.players.is_playing() else False

        self.merged_titles = WINDOW_TITLE_MAP
        self.preview_resolver = GetPreviewPath()
        self._last_hidden_box = None
        self._box_by_pid = {}
        self.on_player_changed = None

        GLib.timeout_add_seconds(1, self._refresh_all)

    def _refresh_all(self):
        self.children = CenterBox(
            start_children=[_make_media_player(self)],
            center_children=[Box(name="vertical-line", orientation="v")],
            end_children=[_make_hierarchy_for_select(self)],
        )
        return True
