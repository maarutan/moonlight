from typing import TYPE_CHECKING, Literal
from fabric.hyprland.widgets import HyprlandWorkspaces as HWorkspaces
from fabric.widgets.box import Box
from fabric.widgets.label import Label

from .core.style_manager import StyleManager
from .core.preview_manager import PreviewManager
from .core.buttons_factory import ButtonsFactory
from .config import ConfigResolver

if TYPE_CHECKING:
    from ...bar import StatusBar


class Workspaces(Box):
    def __init__(self, init_class: "StatusBar") -> None:
        orientation: Literal["h", "v"] = "h" if init_class.is_horizontal() else "v"
        super().__init__(
            name="sb_workspaces-container",
            orientation=orientation,
            v_align="fill",
            h_align="fill",
        )

        if orientation == "h":
            self.add_style_class("sb_workspaces-container-horizontal")
        else:
            self.add_style_class("sb_workspaces-container-vertical")

        self.iclass = init_class
        self.cfg = init_class.confh

        spec = ConfigResolver(self.cfg, orientation).resolve()  # type: ignore
        StyleManager(self.cfg, "status-bar.widgets.workspaces").apply()

        self.preview_manager = PreviewManager(
            init_class=self,
            enabled=spec.preview.enabled,
            event=spec.preview.event,
            click_button=spec.preview.event_click,
            image_size=spec.preview.size,
            max_visible=spec.max_visible,
            missing_behavior=spec.preview.missing_behavior,
        )

        bf = ButtonsFactory(
            orientation=spec.orientation,
            max_visible=spec.max_visible,
            numbering_enabled=spec.numbering_enabled,
            numbering=spec.numbering,
            enable_factory=spec.enable_factory,
            magic_enabled=spec.magic.enabled,
            magic_icon=spec.magic.icon,
            bind_preview=self.preview_manager.bind,
        )

        buttons = bf.initial_buttons()

        workspaces_widget = HWorkspaces(
            name="sb_workspaces",
            invert_scroll=True,
            empty_scroll=True,
            v_align="fill",
            h_align="fill",
            v_expand=True,
            h_expand=True,
            orientation=orientation,
            spacing=0,
            buttons=buttons,
            buttons_factory=bf.factory(),
        )

        if bf.magic_button:
            line = Label("|" if orientation == "h" else "──")

            bf.magic_button.connect("hide", lambda *_: line.hide())
            bf.magic_button.connect("show", lambda *_: line.show())

            wrapper = Box(
                orientation=orientation,
                spacing=6,
                v_align="fill",
                h_align="fill",
            )
            wrapper.children = [workspaces_widget, line, bf.magic_button]
            self.children = [wrapper]
        else:
            self.children = [workspaces_widget]

    def popup_toggle(self, action: Literal["show", "hide"] = "show"):
        self.preview_manager.toggle(action)
