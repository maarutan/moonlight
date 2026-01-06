from typing import TYPE_CHECKING, Literal
from fabric.hyprland.widgets import HyprlandWorkspaces as HWorkspaces
from fabric.widgets.box import Box
from fabric.widgets.label import Label

from .core.preview_manager import PreviewManager
from .core.buttons_factory import ButtonsFactory

if TYPE_CHECKING:
    from ...bar import StatusBar


class WorkspacesWidget(Box):
    def __init__(self, statusbar: "StatusBar") -> None:
        self.statusbar = statusbar
        self.confh = statusbar.confh

        super().__init__(
            name="statusbar-workspaces-container",
            orientation=self.confh.orientation,  # type: ignore
            v_align="fill",
            h_align="fill",
        )

        if self.confh.orientation == "v":
            self.add_style_class("statusbar-workspaces-container-vertical")

        config = self.confh.config_modules["workspaces"]

        self.conf_max_visible = config["max-visible-workspaces"]
        self.conf_factory = config["enable-buttons-factory"]
        self.conf_numbering_enabled = config["numbering-enabled"]
        self.conf_numbering = config["numbering"]
        self.conf_magic = config["magic-workspace"]
        self.conf_preview = config["workspace-preview"]
        self.conf_if_vertical = config["if-vertical"]

        self.preview_manager = PreviewManager(
            workspaces_widget=self,
            enabled=self.conf_preview["enabled"],
            event=self.conf_preview["event"],
            click_button=self.conf_preview["event_click"],
            image_size=self.conf_preview["size"],
            max_visible=self.conf_max_visible,
            missing_behavior=self.conf_preview["missing-behavior"],
        )

        bf = ButtonsFactory(
            orientation=self.confh.orientation,  # type: ignore
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
            name="statusbar-workspaces",
            invert_scroll=True,
            empty_scroll=True,
            v_align="fill",
            h_align="fill",
            v_expand=True,
            h_expand=True,
            orientation=self.confh.orientation,  # type: ignore
            spacing=0,
            buttons=buttons,
            buttons_factory=bf.factory(),
        )

        if bf.magic_button:
            line = Label("|" if self.confh.orientation == "h" else "──")

            bf.magic_button.connect("hide", lambda *_: line.hide())
            bf.magic_button.connect("show", lambda *_: line.show())

            wrapper = Box(
                orientation=self.confh.orientation,  # type: ignore
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
