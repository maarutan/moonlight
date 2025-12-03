from typing import TYPE_CHECKING, Literal
from fabric.hyprland.widgets import HyprlandWorkspaces as HWorkspaces
from fabric.widgets.box import Box
from fabric.widgets.label import Label

from .core.style_manager import StyleManager
from .core.preview_manager import PreviewManager
from .core.buttons_factory import ButtonsFactory

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

        self.conf = init_class

        StyleManager(
            self.conf.confh, f"{self.conf.widget_name}.widgets.workspaces"
        ).apply()
        config = (
            self.conf.confh.get_option(f"{self.conf.widget_name}.widgets.workspaces")
            or {}
        )
        self.conf_style = config.get("style", {})
        self.conf_max_visible = config.get("max-visible-workspaces", 10)
        self.conf_factory = config.get("factory-buttons-enabled", True)
        self.conf_numbering_enabled = config.get("numbering-enabled", True)
        self.conf_numbering = config.get("numbering", [])
        self.conf_magic = config.get("magic-workspace", {})
        self.conf_preview = config.get("workspace-preview", {})
        self.conf_if_vertical = config.get("if-vertical", {})

        self.preview_manager = PreviewManager(
            init_class=self,
            enabled=self.conf_preview.get("enabled", False),
            event=self.conf_preview.get("event", "hover"),
            click_button=self.conf_preview.get("event_click", "right"),
            image_size=self.conf_preview.get("size", 400),
            max_visible=self.conf_max_visible,
            missing_behavior=self.conf_preview.get("missing-behavior", "show"),
        )

        bf = ButtonsFactory(
            orientation=orientation,
            max_visible=self.conf_max_visible,
            numbering_enabled=self.conf_numbering_enabled,
            numbering=self.conf_numbering,
            enable_factory=self.conf_factory,
            magic_enabled=self.conf_magic.get("enabled", False),
            magic_icon=self.conf_magic.get("icon", ""),
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
