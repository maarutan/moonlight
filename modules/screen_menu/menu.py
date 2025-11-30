from typing import Optional
from fabric.widgets.widget import Widget
from fabric.utils import GLib
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.fixed import Fixed

from .config import ScreenMenuConfig
from .core.popup_menu import PopupMenu


widget_name = "screen-menu"
confh = ScreenMenuConfig(widget_name)
enabled = confh.get_option(f"{widget_name}.enabled", True)

if not enabled:
    ScreenMenu = None  # pyright: ignore[reportAssignmentType]
else:

    class ScreenMenu(Window):
        def __init__(
            self,
        ):
            self.confh = confh
            self.widget_name = widget_name

            super().__init__(
                name=widget_name,
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

            self.list_items = self.confh.get_option(f"{self.widget_name}.items", [])
            self.active_popup: Optional[PopupMenu] = None

            self.add_events("button-press")
            self.connect("button-press-event", self.on_click)

            if not enabled:
                self.hide()

            self.show_all()
            self.is_entered_popup = False

        def timer_of_hide(self, widget: Widget, start: bool):
            if not start:
                return False

            def hide_if_not_entered():
                if not self.is_entered_popup:
                    self.popup_menu.remove_style_class("screen-popup-menu-show")
                    self.popup_menu.add_style_class("screen-popup-menu-hide")
                    GLib.timeout_add(200, self.popup_menu.hide)
                return False

            GLib.timeout_add(2000, hide_if_not_entered)
            return True

        def on_click(self, _, event):
            if event.button == 1:
                if self.active_popup and self.active_popup.get_parent():
                    self.fixed.remove(self.active_popup)
                    self.active_popup = None
                return True

            if event.button == 3:
                if self.active_popup and self.active_popup.get_parent():
                    self.fixed.remove(self.active_popup)

                self.popup_menu = PopupMenu(items=self.list_items, init_class=self)
                self.timer_of_hide(self.popup_menu, start=True)

                self.popup_menu.remove_style_class("screen-popup-menu-hide")
                self.popup_menu.add_style_class("screen-popup-menu-show")

                self.popup_menu.show_all()

                min_w, nat_w = self.popup_menu.get_preferred_width()
                min_h, nat_h = self.popup_menu.get_preferred_height()

                alloc = self.get_allocation()
                win_w, win_h = alloc.width, alloc.height

                x = int(event.x) + self.popup_offset_x
                y = int(event.y) + self.popup_offset_y

                if x + nat_w > win_w:
                    x = int(event.x) - nat_w - self.popup_offset_x

                if y + nat_h > win_h:
                    y = int(event.y) - nat_h - self.popup_offset_y

                self.fixed.put(self.popup_menu, x, y)
                self.active_popup = self.popup_menu

                return True

            return False
