from functools import partial
from fabric.widgets.button import Button
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.hyprland.widgets import ActiveWindow
from fabric.utils import FormattedString, GLib, Gtk, truncate  # type: ignore
from utils import WINDOW_TITLE_MAP
from fabric.widgets.box import Box
from typing import Optional
from services import PlayerManager
from .cava import SpectrumRender
from fabric.widgets.label import Label
import unicodedata
from fabric.widgets.grid import Grid
import re


class WindowTitleWidget(Box):
    """A widget that displays the title of the active window."""

    def __init__(
        self,
        orientation_pos: bool = False,
        truncation: bool = True,
        truncation_size: int = 80,
        title_map: Optional[list] = None,
        vertical_title_length: int = 6,
        enable_icon: bool = True,
        **kwargs,
    ):
        self.orientation_pos = orientation_pos
        self.truncation = truncation
        self.truncation_size = truncation_size
        self.title_map = title_map or []
        self.enable_icon = enable_icon
        self.vertical_title_length = vertical_title_length

        self.merged_titles = self.title_map + WINDOW_TITLE_MAP

        super().__init__(name="window-box", **kwargs)

        self.children = Box(
            children=ActiveWindow(
                name="window",
                formatter=FormattedString(
                    "{ get_title(win_title, win_class) }",
                    get_title=self.get_title,
                ),
            )
        )

    def trim_visual(self, text: str, max_width: int) -> str:
        result = ""
        current_width = 0
        for char in text:
            if unicodedata.east_asian_width(char) in ("F", "W"):
                char_width = 2
            else:
                char_width = 1

            if current_width + char_width > max_width:
                break

            result += char
            current_width += char_width

        return result

    def get_title(self, win_title, win_class):
        if self.truncation:
            win_title = truncate(win_title, self.truncation_size)

        win_class_lower = win_class.lower()

        matched_window = next(
            (wt for wt in self.merged_titles if re.search(wt[0], win_class_lower)),
            None,
        )

        if not matched_window:
            return f"  {win_class_lower}"

        title = matched_window[2]
        icon = matched_window[1]

        if not self.enable_icon:
            return title

        if self.orientation_pos:
            return f"{icon} {title}"
        else:
            title = self.trim_visual(title, self.vertical_title_length)
            return f" {icon}\n{title}."


class SmartTitleWidget(Box):
    def __init__(self, **kwargs):
        super().__init__(name="window-box", **kwargs)
        self.player = PlayerManager()
        self.cava_play = SpectrumRender().get_spectrum_box()
        self.title = WindowTitleWidget()
        PlayerHierarchyPopup()

        # if self._is_played():
        # self.children = Box(children=[self.title, self.cava_play])
        # else:
        #     self.children = Box(children=self.title)


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
        self.players = PlayerManager()
        self.merged_titles = WINDOW_TITLE_MAP

        self.children = self._make_hierarchy()

    def _make_hierarchy(self) -> Grid:
        grid = Grid(
            name="player-hierarchy-grid",
            row_spacing=12,
            column_spacing=12,
            column_homogeneous=True,
            row_homogeneous=True,
        )

        _base = dict(self.players._get_playing_players())
        __ordered_players = []
        __ordered_players_box = []
        __retry = []
        __retry_box = []
        _clicked = False

        def __get_new_base(pid, box):
            full = self.players._get_playing_players().values()
            for k, v in _base.items():
                v.pop(pid, None)

            if (not __ordered_players or __ordered_players[0] is None) and (
                not __ordered_players_box or __ordered_players_box[0] is None
            ):
                __ordered_players.append(pid)
                __ordered_players_box.append(box)
            else:
                removed_box_id = __ordered_players[0]
                if removed_box_id != pid:
                    for i in full:
                        for k, v in i.items():
                            if k == removed_box_id:
                                __retry.append(k)
                                break

                    for i in full:
                        for k, v in i.items():
                            if k == __retry[0]:
                                __retry_box.append(dict({k: v}))

            for player_box in __ordered_players_box:
                grid.attach(player_box, col, row, 1, 1)
                grid.show_all()

        def __update(pid, box) -> bool:
            __get_new_base(pid, box)

            try:
                if __retry_box[0]:
                    for key, value in __retry_box[0].items():
                        for k, v in _base.items():
                            v[key] = value
                        break
            except:
                pass

            grid.remove(box)
            return True

        def _players_handler():
            if _clicked:
                return _base
            else:
                return self.players._get_playing_players().values()

        players = _players_handler()

        col_count = 1
        index = col_count

        def __make_on_clicked(pid, box):
            return lambda *_: __update(pid, box)

        for player_group in players:
            for player_id, player_data in player_group.items():
                title = player_data["title"]
                artist = player_data["artist"]

                icon = next(
                    (wt for wt in self.merged_titles if re.search(wt[0], player_id)),
                    "",
                )

                player_box = Box(
                    name="player-card",
                    orientation=Gtk.Orientation.VERTICAL,
                    spacing=4,
                )

                player_box.children = [
                    Box(
                        name="player-popup-icon-container",
                        children=[
                            Label(
                                h_align="start",
                                name="player-popup-icon",
                                label=f"{icon[1]} ",
                            ),
                            Label(
                                h_align="start",
                                name="player-popup-id",
                                label=player_id,
                            ),
                        ],
                    ),
                    Label(
                        name="player-popup-title",
                        label=title[:50] + "..." if len(title) > 10 else title,
                        h_align="start",
                    ),
                    Label(
                        name="player-popup-artist",
                        label=artist,
                        h_align="start",
                    ),
                    Button(
                        name="player-popup-button",
                        label="Choice 🚀",
                        on_clicked=__make_on_clicked(player_id, player_box),
                    ),
                ]

                row = index // col_count
                col = index % col_count

                grid.attach(player_box, col, row, 1, 1)
                index += 1

        return grid
