# components.py

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..media_player_hierarchy_popup import PlayerHierarchyPopup

import re

from fabric.utils import Gtk  # type:ignore
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.grid import Grid
from fabric.widgets.button import Button


def _make_hierarchy(self: "PlayerHierarchyPopup") -> Grid:
    grid = Grid(
        name="player-hierarchy-grid",
        row_spacing=12,
        column_spacing=12,
        column_homogeneous=True,
        row_homogeneous=True,
    )

    self._box_by_pid.clear()

    def __update(pid, box):
        self.selected_player_id = pid
        if self._last_hidden_box and self._last_hidden_box is not box:
            self._last_hidden_box.set_visible(True)
        box.set_visible(False)
        self._last_hidden_box = box

        if self.on_player_changed:
            self.on_player_changed(pid)

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
                    label="Choice 🚀",
                    on_clicked=__make_on_clicked(pid, box),
                ),
            ]

            if pid == self.selected_player_id:
                box.set_visible(False)
                self._last_hidden_box = box

            row = idx // col_count
            col = idx % col_count
            grid.attach(box, col, row, 1, 1)
            idx += 1

    if not self.selected_player_id and self._box_by_pid:
        first_pid = next(iter(self._box_by_pid))
        self.selected_player_id = first_pid
        box = self._box_by_pid[first_pid]
        box.set_visible(False)
        self._last_hidden_box = box
        if self.on_player_changed:
            self.on_player_changed(first_pid)

    return grid
