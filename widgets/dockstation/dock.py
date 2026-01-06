# dockstation.py
from fabric.utils import idle_add
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.box import Box
from fabric.widgets.eventbox import EventBox
from fabric.widgets.revealer import Revealer

from .tools import DockStationTools
from .config import ConfigHandlerDockStation
from .servises.hypr import Hypr
from .core.dock_items.items import DockStationItems
from .core.actions import DockStationActions
from .core.application_browser.application_widget import ApplicationBrowserWidget


config_handler = ConfigHandlerDockStation()
if not config_handler.config["enabled"]:
    DockStation = None  # type: ignore
else:

    class DockStation(Window):
        def __init__(self):
            self.confh = config_handler
            self.actions = DockStationActions(self)
            self.tools = DockStationTools(self)
            self.hypr = Hypr(self)

            self.main_box = Box(
                name=f"dockstation-box",
                orientation="v" if self.confh.orientation == "h" else "h",
                h_align="center",
                v_align="center",
                h_expand=True,
                v_expand=True,
            )

            self.main_event = EventBox(child=EventBox(child=self.main_box))
            self.hover_line = EventBox(name="dockstation-hover-line")
            if self.confh.is_vertical():
                self.hover_line.set_size_request(
                    self.confh.config["hover"]["thickness"],
                    self.confh.config["hover"]["max-width"],
                )
            else:
                self.hover_line.set_size_request(
                    self.confh.config["hover"]["max-width"],
                    self.confh.config["hover"]["thickness"],
                )
            super().__init__(
                name="dockstation",
                anchor=self.confh.config["anchor"],
                layer=self.confh.config["layer"],
                margin=self.confh.config["margin"],
                h_align="center",
                exclusivity="none" if self.confh.config["auto-hide"] else "auto",
                v_align="center",
                h_expand=True,
                v_expand=True,
                keyboard_mode="on-demand",
                child=Box(
                    v_align="fill",
                    h_align="fill",
                    h_expand=True,
                    v_expand=True,
                    orientation="h" if self.confh.orientation == "v" else "v",
                    children=[
                        self.hover_line,
                        self.main_event,
                    ],
                ),
                visible=True,
            )

            self.items = DockStationItems(self)
            self.application_browser = ApplicationBrowserWidget(self)
            self.items._get_toggle(self.application_browser.toggle)

            self.main_box.children = [
                self.items,
                self.application_browser,
            ]

            self.add_keybinding(
                "ctrl i",
                lambda: idle_add(
                    self.application_browser.app_browser.search_entry.grab_focus
                ),
            )
            self.add_keybinding(
                "escape",
                lambda: self.application_browser.on_hide(
                    hamburger=self.items.hamburger
                ),
            )

            if self.confh.is_vertical():
                self.add_style_class("dockstation-vertical")
            if self.confh.config["auto-hide"]:
                self.tools.auto_hide()
                self.hover_line.connect("enter-notify-event", self.tools.hover_enter)
                self.hover_line.connect("leave-notify-event", self.tools.hover_leave)
                self.main_event.connect("enter-notify-event", self.tools.hover_enter)
                self.main_event.connect("leave-notify-event", self.tools.hover_leave)
            else:
                self.tools.toggle("show")
            self.main_event.connect(
                "leave-notify-event",
                lambda: self.application_browser.on_hide(
                    hamburger=self.items.hamburger
                ),
            )
