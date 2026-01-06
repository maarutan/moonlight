from typing import List, Optional, Callable, Literal
from fabric.hyprland.widgets import WorkspaceButton
from utils.widget_utils import setup_cursor_hover
from fabric.widgets.label import Label
from fabric.widgets.box import Box
from fabric.hyprland import Hyprland
from fabric.utils import GLib
import json


class ButtonsFactory:
    def __init__(
        self,
        orientation: Literal["h", "v"],
        max_visible: int,
        numbering_enabled: bool,
        numbering: list[str],
        enable_factory: bool,
        magic_enabled: bool,
        magic_icon: str,
        bind_preview: Optional[Callable[[WorkspaceButton], None]] = None,
    ) -> None:
        self.orientation = orientation
        self.max_visible = max_visible
        self.numbering_enabled = numbering_enabled
        self.numbering = numbering
        self.enable_factory = enable_factory
        self.magic_enabled = magic_enabled
        self.magic_icon = magic_icon
        self.bind_preview = bind_preview
        self.magic_button: Optional[Box] = None
        self.hypr = Hyprland(commands_only=False)

        if self.magic_enabled:
            self._init_magic_button()
            self._connect_events()

    def _init_magic_button(self) -> None:
        self.magic_button = Box(
            name="statusbar-magic-workspace-button",
            v_align="center",
            h_align="center",
            v_expand=True,
            h_expand=True,
            children=Label(label=self.label_for(-1)),
        )
        if self.bind_preview:
            self.bind_preview(self.magic_button)
        if not self._magic_has_windows():
            self.magic_button.hide()

    def _connect_events(self) -> None:
        for ev in (
            "workspace",
            "activewindow",
            "closewindow",
            "openwindow",
            "movewindow",
            "focusedmon",
        ):
            self.hypr.connect(f"event::{ev}", self._on_event)

    def _on_event(self, *_):
        GLib.idle_add(self._update_magic_visibility)

    def _update_magic_visibility(self) -> bool:
        if not self.magic_button:
            return False
        self.magic_button.set_visible(self._magic_has_windows())
        return False

    def label_for(self, i: int) -> str:
        if i < 0:
            return str(self.magic_icon)
        if not self.numbering_enabled:
            return ""
        return self.numbering[i - 1] if i - 1 < len(self.numbering) else str(i)

    def _magic_has_windows(self) -> bool:
        try:
            reply = Hyprland.send_command("j/workspaces")
            if not reply.reply:
                return False
            for ws in json.loads(reply.reply.decode()):
                if (
                    ws.get("id") == -98
                    and ws.get("windows", 0) > 0
                    or ws.get("id") < 0
                    and ws.get("windows", 0) > 0
                ):
                    return True
        except Exception:
            pass
        return False

    def initial_buttons(self) -> List[WorkspaceButton]:
        buttons: List[WorkspaceButton] = []
        for i in range(1, self.max_visible + 1):
            btn = WorkspaceButton(
                id=i,
                label=self.label_for(i),
                style_classes=["buttons-workspace"],
                v_align="center",
                h_align="center",
                v_expand=True,
                h_expand=True,
            )
            if self.bind_preview:
                self.bind_preview(btn)
            setup_cursor_hover(btn)
            buttons.append(btn)
        return buttons

    def factory(self):
        if not self.enable_factory:
            return None

        def _factory(i: int):
            if i < 1:
                return None
            btn = WorkspaceButton(
                id=i,
                label=self.label_for(i),
                style_classes=["buttons-workspace"],
                v_align="center",
                h_align="center",
                v_expand=True,
                h_expand=True,
            )
            if self.bind_preview:
                self.bind_preview(btn)
            GLib.idle_add(self._update_magic_visibility)
            return btn

        return _factory
