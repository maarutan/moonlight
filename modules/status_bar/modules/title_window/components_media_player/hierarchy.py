from pathlib import Path
from typing import TYPE_CHECKING

from config.data import GHOST_IMAGE

if TYPE_CHECKING:
    from ..media_player_hierarchy_popup import PlayerHierarchyPopup

import re

from fabric.utils import GLib, Gtk  # type:ignore
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.grid import Grid
from fabric.widgets.button import Button


def _make_hierarchy(self: "PlayerHierarchyPopup") -> Gtk.ScrolledWindow:
    grid = Grid(
        name="player-hierarchy-grid",
        row_spacing=12,
        column_spacing=12,
        column_homogeneous=True,
        row_homogeneous=True,
        style=f"""
            background-image: url('{Path(GHOST_IMAGE)}');
            background-size: 200px;
            background-repeat: no-repeat;
            background-position: center;
                """,
    )

    self._box_by_pid.clear()

    def __update(pid, box):
        self.selected_player_id = pid

        if self.on_player_changed:
            self.on_player_changed(pid)
        self.players.pause_all_except(pid)

        for p, b in self._box_by_pid.items():
            pin_label = b.get_children()[0].get_children()[2]  # player-popup-pin_sign
            pin_label.set_label("📌" if p == pid else "")

        return True

    def __make_on_clicked(pid, box):
        return lambda *_: __update(pid, box)

    col_count = 1
    idx = 0
    playing = self.players._get_playing_players()

    for group in playing.values():
        for pid, pdata in group.items():
            icon = next(
                (wt for wt in self.merged_titles if re.search(wt[0], pid)),
                (None, ""),
            )[1]

            box = Box(
                name="player-card", orientation=Gtk.Orientation.VERTICAL, spacing=4
            )
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
                    label=pdata["title"][:50]
                    + ("..." if len(pdata["title"]) > 50 else ""),
                    h_align="start",
                ),
                Label(
                    name="player-popup-artist",
                    label=pdata["artist"],
                    h_align="start",
                ),
                Button(
                    name="player-popup-button",
                    label="Select 👈",
                    on_clicked=__make_on_clicked(pid, box),
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

    scrolled = Gtk.ScrolledWindow()
    scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
    scrolled.set_overlay_scrolling(False)
    scrolled.add(grid)
    scrolled.set_min_content_height(500)
    grid.set_size_request(300, 300)

    scrolled.show_all()

    return scrolled
