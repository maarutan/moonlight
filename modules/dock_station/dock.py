from pathlib import Path

from fabric.widgets.box import Box
from fabric.widgets.button import Button
from fabric.widgets.eventbox import EventBox
from fabric.widgets.label import Label
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.hyprland.widgets import get_hyprland_connection
from gi.repository import Gdk, GLib  # type: ignore

from utils import JsonManager
from utils.widget_utils import setup_cursor_hover
from .modules.items import Items
from config import DOCK_MENU_ICON

from .modules.hamburger import HamburgerDrawing
from .modules.dock_tools import DockTools
from .modules.anchor import ANCH_DICT
from .core._config_handler import ConfigHandlerDockStation
from fabric.widgets.svg import Svg
from fabric.widgets.image import Image


class Dock(Window):
    def __init__(
        self,
        enabled: bool = True,
    ) -> None:
        self.confh = ConfigHandlerDockStation()
        super().__init__(
            name="dock-station",
            layer="top",
            anchor=self.confh.dock.anchor() or "bottom center",
            exclusivity="none",
        )

        self.json = JsonManager()
        self.anchor_dock = self.confh.dock.anchor()
        self.menu_icon = self.confh.dock.menu()["icon"]
        self.dock_size = self.confh.dock.size()
        self.menu_type = self.confh.dock.menu()["type"]
        self.menu_pixbuf_path = Path(self.confh.dock.menu()["path"])
        self.menu_position = self.confh.dock.menu()["position"]
        self.anchor_position_dict = ANCH_DICT
        self.is_popup_menu_open = False
        self.dots = self.confh.dock.instance()["icon"]
        self.max_dots = self.confh.dock.instance()["max_items"]
        self.pinned_icon = self.confh.dock.pinned()["pinned"]
        self.unpinned_icon = self.confh.dock.pinned()["unpinned"]
        self.instance_enabled = self.confh.dock.instance()["enabled"]
        print(self.instance_enabled)

        anchor_side = self._anchor_handler()
        self.is_horizontal = anchor_side in ("top", "bottom")

        self.is_dock_hide = True
        self.hide_id = None
        self.dock = DockTools(self)

        self.conn = get_hyprland_connection()
        self.clients_cache = {}
        self.current_ws = 0

        if self.conn.ready:
            GLib.idle_add(self.dock._init_subscriptions)
        else:
            self.conn.connect(
                "event::ready", lambda *_: GLib.idle_add(self.dock._init_subscriptions)
            )

        self.view = Box(name="viewport", orientation="h" if self.is_horizontal else "v")

        self.wrapper = EventBox(
            h_align="center",
            v_align="center",
            v_expand=True,
            h_expand=True,
        )
        self.wrapper.add_events(
            Gdk.EventMask.ENTER_NOTIFY_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK
        )
        self.wrapper.connect("enter-notify-event", self.dock._on_wrapper_enter)
        self.wrapper.connect("leave-notify-event", self.dock._on_wrapper_leave)

        self.content = Box(
            name="dock",
            orientation="h" if self.is_horizontal else "v",
            h_align="fill",
            v_align="fill",
            v_expand=True,
            h_expand=True,
            children=self.view,
        )
        self.wrapper.add(EventBox(child=self.content))

        self.hover = EventBox()
        # if self.is_horizontal:
        #     self.hover.set_size_request(300, 0)
        # else:
        #     self.hover.set_size_request(0, 300)
        if self.is_horizontal:
            self.hover.set_size_request(self.dock_size * 2, 0)
        else:
            self.hover.set_size_request(0, self.dock_size * 2)

        self.hover.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK)
        self.hover.connect("enter-notify-event", self.dock._on_hover_enter)

        self.items = Items(self)

        result_menu = None
        if self.menu_type == "hamburger":
            self.hamburger = HamburgerDrawing()
            self.hamburger_box = Box(
                name="hamburger-box",
                h_align="center",
                v_align="center",
                h_expand=False,
                v_expand=False,
                children=[self.hamburger],
            )
            self.hamburger.show_all()
            self.hamburger_button = Button(
                name="hamburger-button",
                child=self.hamburger_box,
                on_clicked=self._on_hamburger_clicked,
            )
            result_menu = self.hamburger_button
        elif self.menu_type == "svg":
            result_menu = Button(child=Svg(svg_file=self.menu_pixbuf_path.as_posix()))
        elif self.menu_type == "image":
            result_menu = Button(
                child=Image(image_file=self.menu_pixbuf_path.as_posix())
            )
        elif self.menu_type == "icon":
            result_menu = Button(child=Label(label=self.menu_icon))

        if self.menu_position == "left":
            if result_menu:
                setup_cursor_hover(result_menu)
                self.view.add(result_menu)
            setup_cursor_hover(self.items)
            self.view.add(self.items)
        else:
            setup_cursor_hover(self.items)
            self.view.add(self.items)
            if result_menu:
                setup_cursor_hover(result_menu)
                self.view.add(result_menu)

        self.result_menu = result_menu

        if enabled:
            self.main_box = Box(
                orientation="v" if self.is_horizontal else "h",
                children=[self.wrapper, self.hover],
            )
            self.children = self.main_box
            self.dock.auto_hide_check()

    def _on_hamburger_clicked(self, *_):
        self.hamburger.toggle()
        self.is_popup_menu_open = self.hamburger.is_active

    def _update_state(self):
        try:
            self.clients_cache = {
                c["address"]: c
                for c in self.json.loads(
                    self.conn.send_command("j/clients").reply.decode()
                )
            }
            self.current_ws = self.json.loads(
                self.conn.send_command("j/activeworkspace").reply.decode()
            ).get("id", 0)
        except Exception:
            self.clients_cache = {}
            self.current_ws = 0

    def _anchor_handler(self) -> str:
        for key, value in self.anchor_position_dict.items():
            if self.anchor_dock in value:
                return key
        return "bottom"
