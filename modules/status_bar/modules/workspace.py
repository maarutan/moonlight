from fabric.hyprland.widgets import WorkspaceButton
from fabric.hyprland.widgets import Workspaces as HWorkspaces
from fabric.widgets.box import Box

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
    ):
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
