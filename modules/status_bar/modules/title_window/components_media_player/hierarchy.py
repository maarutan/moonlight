from pathlib import Path
from typing import TYPE_CHECKING

# from config.data import GHOST_IMAGE

if TYPE_CHECKING:
    from ..media_player_hierarchy_popup import PlayerHierarchyPopup

import re

from fabric.utils import GLib, Gtk  # type:ignore
from fabric.widgets.scrolledwindow import ScrolledWindow
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.grid import Grid
from fabric.widgets.button import Button


def _make_hierarchy_for_select(self: "PlayerHierarchyPopup") -> Gtk.ScrolledWindow:
    grid = Grid(
        name="player-hierarchy-grid",
        row_spacing=12,
        column_spacing=12,
        column_homogeneous=True,
        row_homogeneous=True,
        style=(
            f"""
    background-image: url('{self.background_path}');
    background-size: {self.ghost_size}px;
    background-repeat: no-repeat;
    background-position: center;
    """
            if self.if_empty_ghost_will_come_out
            else ""
        ),
    )

    self._box_by_pid.clear()

    def __make_on_clicked(pid, box, val):
        return lambda *_: __update(pid, box, val)

    def __update(pid, box, val):
        if not self.selected_player_id and self._box_by_pid:
            first_pid = next(iter(self._box_by_pid))
            self.selected_player_id = first_pid
            if self.on_player_changed:
                self.on_player_changed(first_pid)
        self.selected_player_id = pid
        self.selected_title = val.get("title", None)
        self.selected_artist = val.get("artist", None)
        self.selected_album = val.get("album", None)
        self.selected_preview_image = val.get("arturl", None)

        for p, b in self._box_by_pid.items():
            pin_label = b.get_children()[0].get_children()[2]
            pin_label.set_label("📌" if p == pid else "")

        box.add_class("selected")

        if self.on_player_changed:
            self.on_player_changed(pid)

        if self.single_active_player:
            self.mp.play_pause(pid)

        return True

    col_count = 1
    idx = 0

    for pid, val in self.active_players.items():
        icon = next(
            (wt for wt in self.merged_titles if re.search(wt[0], pid)),
            (None, ""),
        )[1]

        box = Box(name="player-card", orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self._box_by_pid[pid] = box

        box.children = [
            Box(
                name="player-popup-icon-container",
                children=[
                    Label(
                        h_align="start",
                        name="player-popup-icon",
                        label=f"{icon} ",
                    ),
                    Label(h_align="start", name="player-popup-id", label=pid),
                    Label(
                        name="player-popup-pin_sign",
                        label="📌" if pid == self.selected_player_id else "",
                        h_align="end",
                        v_align="start",
                        h_expand=True,
                    ),
                ],
            ),
            Label(
                name="player-popup-title",
                label=val["title"][:50] + ("..." if len(val["title"]) > 50 else ""),
                h_align="start",
            ),
            Label(
                name="player-popup-artist",
                label=val["artist"],
                h_align="start",
            ),
            Button(
                name="player-popup-button",
                label="Select 👈",
                on_clicked=__make_on_clicked(pid, box, val),
            ),
        ]

        row = idx // col_count
        col = idx % col_count
        grid.attach(box, col, row, 1, 1)
        idx += 1

    if not self.selected_player_id and self._box_by_pid:
        first_pid = next(iter(self._box_by_pid))
        self.selected_player_id = first_pid
        if self.on_player_changed:
            self.on_player_changed(first_pid)

    scrolled = ScrolledWindow()
    scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
    scrolled.set_overlay_scrolling(False)
    scrolled.add(grid)
    scrolled.set_min_content_height(500)
    grid.set_size_request(300, 300)

    scrolled.show_all()

    return scrolled
