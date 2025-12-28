from typing import TYPE_CHECKING
from fabric.widgets.box import Box
from fabric.widgets.button import Button
from fabric.utils import Gdk
from modules.dock_station.core.menu.app_menu import build_app_menu
from utils.widget_utils import setup_cursor_hover

if TYPE_CHECKING:
    from ..dock import DockStation


class DockAppButton(Button):
    def __init__(self, conf: "DockStation", app_name: str, icon, indicator):
        self.conf = conf
        self.app_name = app_name

        inner = Box(
            orientation="v",
            h_expand=False,
            v_expand=False,
            h_align="center",
            v_align="center",
            spacing=5,
        )
        inner.add(icon)
        if indicator is not None:
            inner.add(indicator)

        super().__init__(
            name=self.conf.widget_name + "-btn",
            hexpand=True,
            vexpand=True,
            halign="fill",
            valign="fill",
            tooltip_text=app_name,
            child=inner,
        )

        menu = build_app_menu(self.conf, self.app_name)
        menu.connect("deactivate", self.conf.tools.auto_hide)
        menu.connect("selection-done", self.conf.tools.auto_hide)

        def _click_handler(widget, event):
            if event.type == Gdk.EventType.BUTTON_PRESS:
                if event.button == 3:
                    menu.popup(widget)
                    return True
                elif event.button == 1:
                    self.conf.actions.handle_app(
                        self.app_name, self.conf.hypr.windows_for_app(self.app_name)
                    )
                    return True
            return False

        setup_cursor_hover(self)
        self.connect("button-press-event", _click_handler)

        # hover handlers
        self.connect("enter-notify-event", self.conf.tools.hover_enter)
        menu.connect("enter-notify-event", self.conf.tools.hover_enter)
