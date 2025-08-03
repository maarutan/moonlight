from os import name
from typing import TYPE_CHECKING
from config import PLACEHOLDER_IMAGE

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
    block = Box(
        name="player-card",
        orientation=Gtk.Orientation.VERTICAL,
        spacing=4,
    )

    def split_label_smart(text: str) -> str:
        words = text.strip().split()

        if len(words) >= 2 and len(words) % 2 == 0:
            mid = len(words) // 2
            return " ".join(words[:mid]) + "\n" + " ".join(words[mid:])
        else:
            mid_char = len(text) // 2
            return text[:mid_char] + "\n" + text[mid_char:]

    icon = next(
        (wt for wt in self.merged_titles if re.search(wt[0], self.selected_player_id)),
        (None, ""),
    )[1]

    def artist_render() -> str:
        artist = self.players.get_options(self.selected_player_id, "artist", "Unknown")
        if artist in ["", "Unknown", None, False]:
            artist = self.json.get_with_dot_data(
                self.status_bar_lock_modules, "title_plyaer.artist"
            )
            return artist
        else:
            self.json.update(
                self.status_bar_lock_modules, "title_plyaer.artist", artist
            )
            return artist or "Unknown"

    def title_render() -> str:
        title = self.players.get_options(self.selected_player_id, "title", "Unknown")
        if title in ["", "Unknown", None, False]:
            title = self.json.get_with_dot_data(
                self.status_bar_lock_modules, "title_plyaer.title"
            )
            return title
        else:
            self.json.update(self.status_bar_lock_modules, "title_plyaer.title", title)
            return title or "Unknown"

    current_select = Box(
        name="player-popup-current-select",
        orientation=Gtk.Orientation.VERTICAL,
        spacing=2,
        h_align="start",
        children=[
            Box(
                name="player-popup-current-select-icon",
                children=[
                    Label(name="player-popup-player-name", label=f"player:"),
                    Label(
                        name="player-popup-current-select",
                        label=f" {icon} {self.selected_player_id}",
                    ),
                ],
            ),
            Box(
                name="player-popup-current-artist",
                children=[
                    Label(name="player-popup-player-name", label=f"artist:"),
                    Label(
                        name="player-popup-current-select", label=f" {artist_render()}"
                    ),
                ],
            ),
            Box(
                name="player-popup-current-artist",
                children=[
                    Label(name="player-popup-player-name", label=f"title:"),
                    Label(
                        name="player-popup-current-select-title",
                        label=f" {split_label_smart(str(title_render()))}",
                    ),
                ],
            ),
        ],
    )

    art_url: str | None = None

    for pid_list in self.players._get_playing_players().values():
        for k, v in pid_list.items():
            if k == self.selected_player_id:
                art_url = v.get("art_url", "")
                if art_url:
                    self.art_url_base.clear()
                    self.art_url_base.append(art_url)
                break

    preview_box = Box()

    if self.art_url_base and self.art_url_base[0]:
        art_url_check = self.art_url_base[0]
    else:
        art_url_check = ""

    resolved_path = self.preview_resolver.validator(art_url_check)

    try:
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=str(resolved_path),
            width=350,
            height=350,
            preserve_aspect_ratio=True,
        )
        image_widget = Gtk.Image.new_from_pixbuf(pixbuf)
        preview_box.children = preview_box.children + [image_widget]
    except Exception as e:
        logger.warning(f"[PlayerPopup] Failed to load image: {e}")

    player_control = CenterBox(
        name="player-control",
    )

    def make_clickable_button(button: Button, on_double) -> EventBox:
        box = EventBox(
            child=button,
        )
        box.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)

        def handler(_, event):
            if event.type == Gdk.EventType._2BUTTON_PRESS:
                on_double()
            return True

        box.connect("button-press-event", handler)

        return box

    back_button = Button(
        name="player-popup-back-button-secondary",
        label="",
        all_visible=True,
        visible=True,
        on_clicked=lambda *_: self.players.player_backward_seconds(
            self.selected_player_id
        ),
    )
    handled_back_button = make_clickable_button(
        back_button,
        # on_single=lambda: self.players.player_backward_seconds(self.selected_player_id),
        on_double=lambda: self.players.prev_for(self.selected_player_id),
    )

    def icon_handler():
        return "" if self._is_paused else ""

    def _toggle_pause(button):
        if self._is_paused:
            self.players.pause_player(self.selected_player_id)
            self._is_paused = False
        else:
            self.players.play_player(self.selected_player_id)
            self._is_paused = True
        button.set_label(icon_handler())

    pause_button = Button(
        name="player-popup-pause-button",
        label=icon_handler(),
        all_visible=True,
        on_clicked=_toggle_pause,
    )

    forward_button = Button(
        name="player-popup-forward-button-secondary",
        all_visible=True,
        visible=True,
        label="",
        on_clicked=lambda *_: self.players.player_forward_seconds(
            self.selected_player_id
        ),
    )
    handled_forward_button = make_clickable_button(
        forward_button,
        on_double=lambda: self.players.next_for(self.selected_player_id),
    )

    player_control.start_children = handled_back_button
    player_control.center_children = pause_button
    player_control.end_children = handled_forward_button

    progress = Gtk.ProgressBar(
        name="player-popup-progressbar",
        orientation=Gtk.Orientation.HORIZONTAL,
    )

    progress.set_show_text(True)
    progress.set_hexpand(True)

    progress_box = Box(
        name="player-popup-progress",
        orientation=Gtk.Orientation.VERTICAL,
        spacing=0,
        children=[progress],
        h_align="fill",
        v_align="center",
        h_expand=True,
        v_expand=False,
    )

    self._progress = progress
    self._progress_value = 0.0

    def format_time(seconds: float) -> str:
        return f"{int(seconds) // 60}:{int(seconds) % 60:02}"

    def _update_progress():
        pos, dur = self.players.get_progress(self.selected_player_id)
        fraction = pos / dur if dur > 0 else 0.0

        self._progress_value = fraction
        self._progress.set_fraction(fraction)

        if pos == dur:
            self.players.player_backward_seconds(self.selected_player_id, 1)
            self.players.player_forward_seconds(self.selected_player_id, 1)

        if pos != 0.0 and dur != 1.0:
            content = f"{format_time(pos)} / {format_time(dur)}"
            self.json.update(
                self.status_bar_lock_modules, "title_plyaer.progress", content
            )

        else:
            content = (
                self.json.get_with_dot_data(
                    self.status_bar_lock_modules, "title_plyaer.progress"
                )
                or "--:-- / --:--"
            )

        self._progress.set_text(content)
        return True

    GLib.timeout_add(1000, _update_progress)

    block.children = [
        preview_box,
        current_select,
        progress_box,
        player_control,
        Box(name="horizontal-line", orientation="h"),
    ]
    block.show_all()

    return block
