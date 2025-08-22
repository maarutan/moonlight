from typing import Literal
from fabric.hyprland.widgets import WorkspaceButton
from fabric.hyprland.widgets import Workspaces as HWorkspaces
from fabric.widgets.box import Box
from .workspace_preivew import WorkspacesPreview

import gi
from gi.repository import Gdk  # type: ignore


class Workspaces(Box):
    def __init__(
        self,
        numbering_workpieces=None,
        max_visible_workspaces: int = 10,
        is_horizontal: bool = True,
        magic_icon: str = "✨",
        magic_enable: bool = False,
        enable_buttons_factory: bool = True,
        preview_enable: bool = True,
        preview_image_size: int = 300,
        preview_anchor_handler: str = "top left",
        preview_margin_handler: str = "0 30 0 30",
    ):
        self.is_popup_show = False
        if preview_enable:
            self.popup = WorkspacesPreview(
                image_size=preview_image_size,
                anchor_handler=preview_anchor_handler,
                margin_handler=preview_margin_handler,
                max_visible_workspaces=max_visible_workspaces,
            )
            self.popup.hide()
        else:
            self.popup = None

        if numbering_workpieces is None:
            numbering_workpieces = []

        def get_label(i: int) -> str:
            if i < 0:
                return magic_icon
            return (
                numbering_workpieces[i - 1]
                if i - 1 < len(numbering_workpieces)
                else str(i)
            )

        def set_pointer_cursor(widget):
            gdk_window = widget.get_window()
            if gdk_window:
                display = Gdk.Display.get_default()
                cursor = Gdk.Cursor.new_from_name(display, "pointer")
                gdk_window.set_cursor(cursor)

        def custom_buttons_factory(i: int):
            if i < 0 and magic_enable:
                btn = WorkspaceButton(
                    id=i,
                    label=magic_icon,
                    style_classes=["magic-workspace"],
                    orientation="h" if is_horizontal else "v",
                    v_align="fill",
                    h_align="fill",
                    v_expand=True,
                    h_expand=True,
                )
            elif i >= 1 and enable_buttons_factory:
                btn = WorkspaceButton(
                    id=i,
                    v_expand=True,
                    h_expand=True,
                    v_align="fill",
                    h_align="fill",
                    label=str(i),
                    style_classes=["buttons-workspace"],
                )
            else:
                return None
            btn.connect("realize", lambda w: set_pointer_cursor(w))
            btn.connect("enter-notify-event", self._on_enter)
            btn.connect("leave-notify-event", self._on_leave)
            return btn

        buttons = []
        for i in range(1, max_visible_workspaces + 1):
            btn = WorkspaceButton(
                v_align="fill",
                h_align="fill",
                id=i,
                label=get_label(i),
                style_classes=["buttons-workspace"],
            )
            btn.connect("realize", lambda w: set_pointer_cursor(w))
            btn.connect("enter-notify-event", self._on_enter)
            btn.connect("leave-notify-event", self._on_leave)
            buttons.append(btn)

        super().__init__(
            name="statusbar-workspaces-container",
            orientation="h" if is_horizontal else "v",
            v_align="fill",
            h_align="fill",
        )

        workspaces_widget = HWorkspaces(
            name="statusbar-workspaces-text",
            invert_scroll=True,
            empty_scroll=True,
            v_align="fill",
            h_align="fill",
            v_expand=True,
            h_expand=True,
            orientation="h" if is_horizontal else "v",
            spacing=0,
            buttons=buttons if numbering_workpieces else None,
            buttons_factory=custom_buttons_factory if enable_buttons_factory else None,
        )

        self.children = [workspaces_widget]

    def popup_toggle(
        self,
        action: Literal[
            "show",
            "hide",
        ] = "show",
    ):
        if self.popup is None:
            return

        if action == "show" and not self.is_popup_show:
            # self.popup.set_update()
            self.popup.show_all()
            self.is_popup_show = True
        elif action == "hide" and self.is_popup_show:
            self.popup.hide()
            self.is_popup_show = False

    def _on_enter(self, widget, event):
        if self.popup is None:
            return

        ws_id = widget.id
        self.popup.set_update(ws_id)  # type: ignore
        self.popup_toggle("show")

    def _on_leave(self, widget, event):
        if self.popup is None:
            return

        self.popup_toggle("hide")
