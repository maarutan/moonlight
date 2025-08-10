from fabric.widgets.stack import Stack
from .media_player_hierarchy_popup import PlayerHierarchyPopup
from .windows_title import WindowsTitle
from ..cava import SpectrumRender

import re
from utils import WINDOW_TITLE_MAP
from services import MprisPlayer, MprisPlayerManager

from fabric.widgets.eventbox import EventBox
from fabric.widgets.button import Button
from fabric.widgets.label import Label
from fabric.widgets.box import Box
from fabric.utils import GLib, Gdk  # type: ignore


class MPWitWindowsTitle(Box):
    def __init__(
        self,
        title: WindowsTitle,
        background_path: str,
        is_horizontal: bool = True,
        ghost_size: int = 200,
        single_active_player: bool = True,
        if_empty_ghost_will_come_out: bool = True,
        **kwargs,
    ):
        self.is_horizontal = is_horizontal
        self.cava = SpectrumRender(self.is_horizontal)
        self.title = title

        self.active_players = {}  # player_name -> MprisPlayer instance

        self.mpm = MprisPlayerManager()
        self.mpm.connect("player-appeared", self._on_player_appeared)
        self.mpm.connect("player-vanished", self._on_player_vanished)

        for player in self.mpm.players:  # type:ignore
            self.mp = MprisPlayer(player)
            self.player = self.mp.player_name
            self._add_player(player)

        self.popup = PlayerHierarchyPopup(
            ghost_size=ghost_size,
            single_active_player=single_active_player,
            if_empty_ghost_will_come_out=if_empty_ghost_will_come_out,
            background_path=background_path,
            active_players=self.active_players,
            # mpris_player=self.mp,
        )

        self.merged_titles = WINDOW_TITLE_MAP or []
        self.player_popup_state = False
        self._hover_inside = False
        self._popup_hover = False

        super().__init__(
            name="window-box",
            orientation="h" if self.is_horizontal else "v",
            **kwargs,
        )

        self.popup.selected_player_id = next(iter(self.active_players), "")
        self.playing = False
        if (
            self.popup.selected_player_id
            and self.popup.selected_player_id in self.active_players
        ):
            self.playing = (
                self.active_players[self.popup.selected_player_id].playback_status
                == "playing"
            )

        self.icon = next(
            (
                wt
                for wt in self.merged_titles
                if re.search(wt[0], self.popup.selected_player_id)
            ),
            (None, ""),
        )[1]

        self.player_icon_label = Label(name="player-icon", label=f" {self.icon} ")
        self.popup_button = self._create_popup_button()

        self.dynamic_inner = Box(
            orientation="h" if self.is_horizontal else "v",
            children=[self.player_icon_label, self.popup_button],
        )

        self.hover_area = EventBox(
            events=["enter-notify", "leave-notify"],
            child=self.dynamic_inner,
        )
        self.hover_area.connect("enter-notify-event", self._on_mouse_enter)
        self.hover_area.connect("leave-notify-event", self._on_mouse_leave)

        self.popup.connect("enter-notify-event", self._on_popup_enter)
        self.popup.connect("leave-notify-event", self._on_popup_leave)

        self.player_box = Box(
            orientation="h" if self.is_horizontal else "v",
            children=[self.hover_area],
        )
        self.player_container = Box(
            orientation="h" if self.is_horizontal else "v",
            show_all=True,
            children=[self.player_box, Stack(children=[self.cava.get_spectrum_box()])],
        )

        self.main_container = Box(
            orientation="h" if self.is_horizontal else "v",
        )
        self.children = self.main_container
        self.main_container.show_all()

        self._is_playing = None
        self._last_state = None

        self.popup.on_player_changed = self._on_player_changed  # type: ignore

        self._update_children()
        GLib.idle_add(self.popup_button.hide)
        GLib.timeout_add_seconds(1, self._update_children)

    def _add_player(self, player):
        mp = MprisPlayer(player)
        self.active_players[mp.player_name] = mp
        mp.connect("changed", self._on_player_changed)

    def _remove_player(self, player_name):
        mp = self.active_players.pop(player_name, None)
        if mp:
            mp.disconnect_by_func(self._on_player_changed)

    def _on_player_appeared(self, manager, player):
        self._add_player(player)
        GLib.idle_add(self._update_children)

    def _on_player_vanished(self, manager, player_name):
        self._remove_player(player_name)
        GLib.idle_add(self._update_children)

    def _create_popup_button(self):
        self.popup.hide()

        def toggle_popup(_):
            self.player_popup_state = not self.player_popup_state
            self._update_popup_button_icon()

            if self.player_popup_state:
                self.popup.show_all()
            else:
                self.popup.hide()

        return Button(
            name="player-popup-button",
            label="",
            on_clicked=toggle_popup,
        )

    def _on_mouse_enter(self, *_):
        self._hover_inside = True
        self.popup_button.show()

    def _on_mouse_leave(self, *_):
        def delayed_hide():
            if not self._hover_inside and not self.player_popup_state:
                self.popup_button.hide()
            return False

        self._hover_inside = False
        GLib.timeout_add(200, delayed_hide)

    def _on_popup_enter(self, *_):
        self._popup_hover = True
        self.popup.show()

    def _on_popup_leave(self, widget, event: Gdk.EventCrossing):
        if event.detail == Gdk.NotifyType.INFERIOR:
            return False

        self.popup.hide()
        self.popup_button.hide()

        def delayed_hide():
            if not self._hover_inside and not self._popup_hover:
                self.player_popup_state = False
                self._update_popup_button_icon()
                self.popup.hide()
            return False

        self._popup_hover = False
        GLib.timeout_add(200, delayed_hide)
        return True

    def _update_popup_button_icon(self):
        icon = "" if self.player_popup_state else ""
        self.popup_button.set_label(icon)
        self.popup_button.queue_draw()

    def _on_player_changed(self, player, *args):
        GLib.idle_add(self._update_children)

    def _update_children(self, *_):
        playing_players = [
            p for p in self.active_players.values() if p.playback_status == "playing"
        ]

        if playing_players:
            active = playing_players[0]
            pid = active.player_name
            playing = True
        else:
            pid = self.popup.selected_player_id
            playing = False

        icon = next(
            (
                wt[1]
                for wt in self.merged_titles
                if isinstance(wt, (list, tuple))
                and len(wt) >= 2
                and re.search(wt[0], pid)
            ),
            "",
        )

        matched_window = next(
            (wt for wt in self.merged_titles if re.search(wt[0], pid)),
            None,
        )

        new_state = (playing, pid, icon)
        if new_state == self._last_state:
            return True
        self._last_state = new_state

        self._is_playing = playing
        self.player_icon_label.set_text(f" {icon} ")

        # if (
        #     not self._hover_inside
        #     and not self._popup_hover
        #     and not self.player_popup_state
        # ):
        #   self.popup_button.hide()

        self.main_container.show_all()
        self.popup_button.hide()

        self.main_container.children = [
            self.player_container if playing else getattr(self, "title_box", self.title)
        ]

        return True
