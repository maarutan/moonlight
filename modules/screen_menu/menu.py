from typing import Optional
from fabric.widgets.eventbox import EventBox
from gi.repository import Gdk  # type: ignore
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.fixed import Fixed
from .core.popup_menu import PopupMenu


class ScreenMenu(Window):
    def __init__(
        self,
        enabled: bool = True,
        list_items: Optional[list[dict]] = None,
    ):
        super().__init__(
            name="screen-menu",
            exclusivity="auto",
            layer="bottom",
            anchor="top left bottom right",
            style="background: none;",
        )
        self.popup_offset_x = 12
        self.popup_offset_y = 8

        self.set_default_size(600, 400)

        self.fixed = Fixed()
        self.add(self.fixed)

        self.list_items = list_items
        self.active_popup: Optional[PopupMenu] = None
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.drag_widget = None

        self.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.POINTER_MOTION_MASK
            | Gdk.EventMask.BUTTON_RELEASE_MASK
        )

        self.connect("button-press-event", self.on_click)
        self.connect("motion-notify-event", self.on_motion)
        self.connect("button-release-event", self.on_release)

        if not enabled:
            self.hide()

        self.show_all()

    def on_click(self, widget, event):
        popup_menu = PopupMenu(self.list_items)
        if event.button == 3:
            if self.active_popup and self.active_popup.get_parent():
                self.fixed.remove(self.active_popup)

            popup_menu.show_all()

            min_w, nat_w = popup_menu.get_preferred_width()
            min_h, nat_h = popup_menu.get_preferred_height()

            alloc = self.get_allocation()
            win_w, win_h = alloc.width, alloc.height

            x = int(event.x) + self.popup_offset_x
            y = int(event.y) + self.popup_offset_y

            if x + nat_w > win_w:
                x = int(event.x) - nat_w - self.popup_offset_x

            if y + nat_h > win_h:
                y = int(event.y) - nat_h - self.popup_offset_y

            self.fixed.put(popup_menu, x, y)

            self.active_popup = popup_menu
            self.drag_widget = popup_menu

        elif event.button == 1 and self.drag_widget:
            self.dragging = True
            self.drag_offset_x = event.x_root
            self.drag_offset_y = event.y_root

        return True

    def on_motion(self, widget, event):
        if self.dragging and self.drag_widget:
            dx = int(event.x_root - self.drag_offset_x)
            dy = int(event.y_root - self.drag_offset_y)
            alloc = self.drag_widget.get_allocation()
            self.fixed.move(self.drag_widget, alloc.x + dx, alloc.y + dy)
            self.drag_offset_x = event.x_root
            self.drag_offset_y = event.y_root
        return True

    def on_release(self, widget, event):
        if event.button == 1:
            self.dragging = False
        return True
