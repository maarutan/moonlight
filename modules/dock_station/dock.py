from typing import Literal
from fabric.widgets.box import Box
from fabric.widgets.eventbox import EventBox
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.label import Label
from modules.corners import MyCorner

from gi.repository import GLib, Gdk  # type: ignore


class Dock(Window):
    def __init__(self) -> None:
        super().__init__(
            name="dock-station",
            layer="top",
            anchor="bottom center",
            exclusivity="none",
        )
        self.is_dock_hide = False
        self.hide_id = None
        self.is_horizontal = True

        self.view = Box(name="viewport", orientation="h")
        self.wrapper = Box(
            name="dock",
            orientation="v",
            children=[self.view],
        )

        self.hover = EventBox()
        if self.is_horizontal:
            self.hover.set_size_request(300, 0)
        else:
            self.hover.set_size_request(10, 300)
        self.hover.add_events(
            Gdk.EventMask.ENTER_NOTIFY_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK
        )

        self.view = Box(name="viewport", orientation="h")
        self.view.add_events(
            Gdk.EventMask.ENTER_NOTIFY_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK
        )

        self.hover.connect("enter-notify-event", self._on_hover_enter)
        self.hover.connect("leave-notify-event", self._on_hover_leave)

        self.view.connect("enter-notify-event", self._on_hover_enter)
        self.view.connect("leave-notify-event", self._on_hover_leave)

        # self.wrapper.add(Label(label="a;sdfja;sldkfj;asdkf"))

        self.main_box = Box(
            orientation="v",
            children=[
                self.wrapper,
                self.hover,
            ],
        )
        self.toggle_dock("hide")
        self.children = [
            self.main_box,
        ]

    def toggle_dock(
        self,
        action: Literal[
            "show",
            "hide",
        ],
    ):
        if action == "show" and self.is_dock_hide:
            self.is_dock_hide = False
            self.wrapper.add_style_class("dock-station-show")
            self.wrapper.remove_style_class("dock-station-hide")
        elif action == "hide" and not self.is_dock_hide:
            self.is_dock_hide = True
            self.wrapper.add_style_class("dock-station-hide")
            self.wrapper.remove_style_class("dock-station-show")

    def _on_hover_enter(self, *_):
        self.toggle_dock("show")

    def _on_hover_leave(self, *_):
        self.delay_hide()

    def delay_hide(self):
        if self.hide_id:
            GLib.source_remove(self.hide_id)
        self.hide_id = GLib.timeout_add(2000, self.hide_dock)

    def hide_dock(self):
        self.toggle_dock("hide")
        self.hide_id = None
        return False
