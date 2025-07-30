from fabric.widgets.button import Button
from fabric.widgets.eventbox import EventBox
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.hyprland.widgets import ActiveWindow
from fabric.utils import FormattedString, GLib, Gdk, Gtk, truncate  # type: ignore
from utils import WINDOW_TITLE_MAP
from fabric.widgets.box import Box
from typing import Optional
from services import PlayerManager
from .cava import Cava, SpectrumRender
from fabric.widgets.label import Label
import unicodedata
from fabric.widgets.grid import Grid
import re


class WindowTitleWidget(Box):
    """A widget that displays the title of the active window."""

    def __init__(
        self,
        orientation_pos: bool = True,
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
        self._last_hidden_box = None
        self.selected_player_id = ""
        self._box_by_pid = {}  # сохраняем соответствие pid → box
        self.on_player_changed = None
        self.children = [self._make_hierarchy()]
        GLib.timeout_add_seconds(1, self._refresh_hierarchy)

    def _refresh_hierarchy(self):
        self.children = [self._make_hierarchy()]
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

                # Прячем box, если он был выбран ранее
                if pid == self.selected_player_id:
                    box.set_visible(False)
                    self._last_hidden_box = box

                row = idx // col_count
                col = idx % col_count
                grid.attach(box, col, row, 1, 1)
                idx += 1

        # Если нет сохранённого выбора — выбираем первый попавшийся
        if not self.selected_player_id and self._box_by_pid:
            first_pid = next(iter(self._box_by_pid))
            self.selected_player_id = first_pid
            box = self._box_by_pid[first_pid]
            box.set_visible(False)
            self._last_hidden_box = box
            if self.on_player_changed:
                self.on_player_changed(first_pid)

        return grid


class SmartTitleWidget(Box):
    def __init__(self, **kwargs):
        super().__init__(name="window-box", **kwargs)

        self.cava = SpectrumRender()
        self.player = PlayerManager()
        self.title = WindowTitleWidget()
        self.popup = PlayerHierarchyPopup()
        self.merged_titles = WINDOW_TITLE_MAP
        self.player_popup_state = False

        self._hover_inside = False
        self.icon = next(
            (
                wt
                for wt in self.merged_titles
                if re.search(wt[0], self.popup.selected_player_id)
            ),
            (None, ""),
        )[1]

        self.title_box = Box(children=[self.title])
        self.player_icon_label = Label(name="player-icon", label=f" {self.icon} ")
        self.popup_button = self._create_popup_button()

        self.dynamic_inner = Box(children=[self.player_icon_label, self.popup_button])
        GLib.idle_add(self.popup_button.hide)

        self.hover_area = EventBox(
            events=["enter-notify", "leave-notify"],
            child=self.dynamic_inner,
        )
        self.hover_area.connect("enter-notify-event", self._on_mouse_enter)
        self.hover_area.connect("leave-notify-event", self._on_mouse_leave)

        self.player_box = Box(children=[self.hover_area])
        self.player_container = Box(
            show_all=True, children=[self.player_box, self.cava.get_spectrum_box()]
        )

        self.main_container = Box()
        self.children = self.main_container

        self._is_playing = None
        self._last_state = None

        self.player.add_status_callback(self._update_children)
        self.popup.on_player_changed = self._on_player_changed  # type: ignore

        self.popup_button.hide()
        self._update_children()
        GLib.timeout_add_seconds(1, self._update_children)

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
        # используем GLib.timeout, чтобы дать шанс нажать
        def delayed_hide():
            if not self._hover_inside and not self.player_popup_state:
                self.popup_button.hide()
            return False

        self._hover_inside = False
        GLib.timeout_add(200, delayed_hide)

    def _update_popup_button_icon(self):
        icon = "" if self.player_popup_state else ""
        self.popup_button.set_label(icon)
        self.popup_button.queue_draw()

    def _on_player_changed(self, pid):
        icon = next(
            (wt for wt in self.merged_titles if re.search(wt[0], pid)), (None, "")
        )[1]
        self.player_icon_label.set_text(f" {icon} ")

    def _update_children(self, *_):
        self.player._refresh_players()
        playing = self.player.is_any_playing()
        playing_dict = self.player._get_playing_players()

        current_pids = set(pid for group in playing_dict.values() for pid in group)
        pid = self.popup.selected_player_id or ""
        icon = next(
            (wt for wt in self.merged_titles if re.search(wt[0], pid)), (None, "")
        )[1]

        new_state = (playing, pid, icon)
        if new_state == self._last_state:
            return True
        self._last_state = new_state

        self._is_playing = playing

        if playing:
            if self.popup.selected_player_id not in current_pids:
                first_group = next(iter(playing_dict.values()), {})
                first_pid = next(iter(first_group), "")
                if first_pid:
                    self.popup._refresh_hierarchy()
                    self.popup.set_selected_player(first_pid)

        self.player_icon_label.set_text(f" {icon} ")
        self.main_container.show_all()
        self.popup_button.hide()
        self.main_container.children = [
            self.player_container if playing else self.title_box
        ]

        return True
