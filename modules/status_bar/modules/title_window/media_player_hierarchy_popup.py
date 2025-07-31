# player_hierarchy_popup.py

from loguru import logger
from utils import WINDOW_TITLE_MAP
from services import PlayerManager

import re
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.grid import Grid
from fabric.widgets.button import Button
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.utils import GLib, GdkPixbuf, Gtk  # type: ignore
from fabric.widgets.centerbox import CenterBox
from utils import GetPreviewPath


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

        self.players = PlayerManager()
        self.merged_titles = WINDOW_TITLE_MAP
        self.preview_resolver = GetPreviewPath()
        self._last_hidden_box = None
        self._box_by_pid = {}
        self.on_player_changed = None
        self.children = [self._make_hierarchy()]
        GLib.timeout_add_seconds(1, self._refresh_hierarchy)

    def _refresh_hierarchy(self):
        self.children = CenterBox(
            start_children=[self._make_player()],
            end_children=[self._make_hierarchy()],
        )
        return True

    def set_selected_player(self, pid: str):
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

    def _make_player(self):
        block = Box(
            name="player-card",
            orientation=Gtk.Orientation.VERTICAL,
            spacing=4,
        )

        icon = next(
            (
                wt
                for wt in self.merged_titles
                if re.search(wt[0], self.selected_player_id)
            ),
            (None, ""),
        )[1]

        current_select = Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=2,
            h_align="start",
            children=[
                Label(
                    name="player-popup-icon",
                    label=f"player: {icon} {self.selected_player_id}",
                    # xalign=0.0,
                ),
            ],
        )

        art_url: str | None = None

        for pid_list in self.players._get_playing_players().values():
            for k, v in pid_list.items():
                if k == self.selected_player_id:
                    art_url = v.get("art_url", "")

        preview_box = Box()

        if art_url:
            resolved_path = self.preview_resolver.validator(art_url)

            if resolved_path and resolved_path.exists():
                try:
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                        filename=str(resolved_path),
                        width=250,
                        height=250,
                        preserve_aspect_ratio=True,
                    )
                    image_widget = Gtk.Image.new_from_pixbuf(pixbuf)
                    preview_box.children = preview_box.children + [image_widget]
                except Exception as e:
                    logger.warning(f"[PlayerPopup] Failed to load image: {e}")

        player_control = CenterBox()
        pause_button = False

        def _toggle_pause(button):
            if self.players.pause_player(self.selected_player_id):
                self.players.play_player(self.selected_player_id)
                button.label = ""
            else:
                self.players.pause_player(self.selected_player_id)
                button.label = ""

        pause_button = Button(
            name="player-popup-pause-button",
            label="",  # default
            on_clicked=_toggle_pause,
        )

        back_button = Button(
            name="player-back",
            label="",
            on_clicked=lambda *_: self.set_selected_player(""),
        )
        pause_button = Button(name="player-pause", label="", on_clicked=_toggle_pause)
        forward_button = Button(
            name="player-forward",
            label="",
            on_clicked=lambda *_: self.set_selected_player("next"),
        )

        player_control.start_children = [back_button]
        player_control.center_children = [pause_button]
        player_control.end_children = [forward_button]

        block.children = [
            preview_box,
            current_select,
            player_control,
        ]
        block.show_all()

        return block

    def _make_hierarchy(self) -> Grid:
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
