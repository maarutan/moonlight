from typing import Optional
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

        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.on_click)

        if not enabled:
            self.hide()

        self.show_all()

    def on_click(self, widget, event):
        if event.button == 1:
            if self.active_popup and self.active_popup.get_parent():
                self.fixed.remove(self.active_popup)
                self.active_popup = None
            return True

        if event.button == 3:
            if self.active_popup and self.active_popup.get_parent():
                self.fixed.remove(self.active_popup)

            popup_menu = PopupMenu(self.list_items)
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

            return True

        return False
