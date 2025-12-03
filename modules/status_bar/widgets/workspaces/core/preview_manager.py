from typing import TYPE_CHECKING, Optional, Literal
from fabric.utils.helpers import GLib
from fabric.hyprland.service import Hyprland

from ..modules.preview import WorkspacesPreview

from utils.events import event_close_popup
from utils.widget_utils import bar_margin_handler, bar_anchor_handler


if TYPE_CHECKING:
    from ..workspaces import Workspaces


class PreviewManager:
    def __init__(
        self,
        enabled: bool,
        event: Literal["hover", "click"],
        click_button: Literal["left", "middle", "right"],
        image_size: int,
        max_visible: int,
        missing_behavior: str,
        init_class: "Workspaces",
    ) -> None:
        self.enabled = enabled
        self.event = event
        self.click_button = click_button
        self._hovering = False
        self._hover_timeout_id = 0
        self.is_popup_show = False
        self.conf = init_class
        self.hypr = Hyprland()
        self.popup: Optional[WorkspacesPreview] = None

        if enabled:
            self.popup = WorkspacesPreview(
                image_size=image_size,
                anchor_handler=self.preview_anchor_handler(),
                margin_handler=self.preview_margin_handler(),
                max_visible_workspaces=max_visible,
                missing_behavior=missing_behavior,  # type: ignore
            )
            self.popup._hide_window()
        event_close_popup(lambda: self.toggle("hide"))

    def bind(self, btn) -> None:
        if not self.enabled or self.popup is None:
            return
        if self.event == "hover":
            btn.connect("enter-notify-event", self._on_enter)
            btn.connect("leave-notify-event", self._on_leave)
        else:
            btn.connect("button-press-event", self._on_click)
            btn.connect("leave-notify-event", self._on_leave)

    def toggle(self, action: Literal["show", "hide"] = "show") -> None:
        if not self.enabled or self.popup is None:
            return
        if action == "show" and not self.is_popup_show:
            self.popup._show_window()
            if not getattr(self.popup, "_suspended", False):
                self.is_popup_show = True
        elif action == "hide" and self.is_popup_show:
            self.popup._hide_window()
            self.is_popup_show = False

    def _start_hide_timeout(self) -> None:
        if self._hover_timeout_id:
            GLib.source_remove(self._hover_timeout_id)
        self._hover_timeout_id = GLib.timeout_add(150, self._hide_if_no_hover)

    def _cancel_hide_timeout(self) -> None:
        if self._hover_timeout_id:
            try:
                GLib.source_remove(self._hover_timeout_id)
            except Exception:
                pass
            self._hover_timeout_id = 0

    def _hide_if_no_hover(self):
        self._hover_timeout_id = 0
        if not self._hovering:
            self.toggle("hide")
        return False

    def _on_enter(self, widget, event):
        if not self.popup:
            return
        self._hovering = True
        ws_id = getattr(widget, "id", None)
        if ws_id is None:
            return
        self.popup.set_update(ws_id)
        self._cancel_hide_timeout()
        self.toggle("show")

    def _on_leave(self, widget, event):
        if not self.popup:
            return
        self._hovering = False
        self._start_hide_timeout()

    def _on_click(self, widget, event):
        if not self.popup:
            return
        btn_code = (
            1
            if self.click_button == "left"
            else 2
            if self.click_button == "middle"
            else 3
        )
        if getattr(event, "button", None) != btn_code:
            return
        ws_id = getattr(widget, "id", None)
        if ws_id is None:
            return
        self.popup.set_update(ws_id)
        self.toggle("show")

    def preview_anchor_handler(self) -> str:
        dflt = "top left"
        position = self.conf.conf.confh.get_option(
            f"{self.conf.conf.widget_name}.position", "top"
        ).lower()
        layout_config = self.conf.conf.confh.get_option(
            f"{self.conf.conf.widget_name}.widgets.layout", {}
        )
        section = "start"
        for sec_name, widgets in layout_config.items():
            for w in widgets:
                if isinstance(w, str) and "workspaces" in w:
                    section = sec_name
                    break
        anchors = {
            "start": {
                "top": "top left",
                "bottom": "bottom left",
                "left": "top left",
                "right": "top right",
            },
            "center": {
                "top": "top center",
                "bottom": "bottom center",
                "left": "center left",
                "right": "center right",
            },
            "end": {
                "top": "top right",
                "bottom": "bottom right",
                "left": "bottom left",
                "right": "bottom right",
            },
        }
        return anchors.get(section, {}).get(position, dflt)

    def preview_margin_handler(self) -> str:
        return bar_margin_handler(
            position=self.conf.conf.confh.get_option(
                f"{self.conf.conf.widget_name}.position", "top"
            ).lower(),
            layout_config=self.conf.conf.confh.get_option(
                f"{self.conf.conf.widget_name}.widgets.layout", {}
            ),
            default_value="top-left",
            widget_name="workspaces",
            px=30,
        )

    def preview_anchor_handler(self) -> str:
        return bar_anchor_handler(
            position=self.conf.conf.confh.get_option(
                f"{self.conf.conf.widget_name}.position", "top"
            ).lower(),
            layout_config=self.conf.conf.confh.get_option(
                f"{self.conf.conf.widget_name}.widgets.layout", {}
            ),
            default_value="top-left",
            widget_name="workspaces",
        )
