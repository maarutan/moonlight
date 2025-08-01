from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..media_player_hierarchy_popup import PlayerHierarchyPopup

from loguru import logger
import re

from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.utils import Gdk, GdkPixbuf, Gtk  # type: ignore
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.eventbox import EventBox


def _make_selected_player_view(self: "PlayerHierarchyPopup"):
    block = Box(
        name="player-card",
        orientation=Gtk.Orientation.VERTICAL,
        spacing=4,
    )

    icon = next(
        (wt for wt in self.merged_titles if re.search(wt[0], self.selected_player_id)),
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

    if self.art_url_base:
        resolved_path = self.preview_resolver.validator(self.art_url_base[0])
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

    # ---------- Управление плеером ----------
    player_control = CenterBox()

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

    # ← Назад
    back_button = Button(
        name="player-popup-back-button-secondary",
        label="",
        on_clicked=lambda *_: self.players.player_backward_seconds(
            self.selected_player_id
        ),
    )
    handled_back_button = make_clickable_button(
        back_button,
        # on_single=lambda: self.players.player_backward_seconds(self.selected_player_id),
        on_double=lambda: self.players.prev_player(self.selected_player_id),
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

    # → Вперёд
    forward_button = Button(
        name="player-popup-forward-button-secondary",
        label="",
        on_clicked=lambda *_: self.players.player_forward_seconds(
            self.selected_player_id
        ),
    )
    handled_forward_button = make_clickable_button(
        forward_button,
        on_double=lambda: self.players.next_player(self.selected_player_id),
    )

    # Установка кнопок
    player_control.start_children = [handled_back_button]
    player_control.center_children = [pause_button]
    player_control.end_children = [handled_forward_button]

    block.children = [
        preview_box,
        current_select,
        player_control,
    ]
    block.show_all()

    return block
