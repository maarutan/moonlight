from typing import TYPE_CHECKING
from fabric.widgets.box import Box
from fabric.widgets.button import Button
from fabric.utils import Gdk, GLib, idle_add
from utils.widget_utils import set_cursor_now, setup_cursor_hover
from .wiggle_anims import Wiggle
from .appcontextmenu import AppContextMenu
from .button_handler import ButtonHandler

if TYPE_CHECKING:
    from .items import DockStationItems


class DockAppButton:
    def __init__(self, dockstation_items: "DockStationItems"):
        self.items = dockstation_items
        self.dockstation = dockstation_items.dockstation
        self.app_name = None
        self.btn = None
        self._wiggle = None
        self.appcontextmenu = None
        self.buttonh = None
        self._selected = False
        self._dragging = False
        self._long_press_handle = None
        self._long_press_triggered = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.drag_offset = 0

    def _on_long_press_triggered(self):
        self._long_press_triggered = True
        self._dragging = True
        self.buttonh._raise_icon(self.btn)  # type: ignore

        set_cursor_now(self.btn, "grub")
        setup_cursor_hover(self.btn, "grab")
        pointer = Gdk.Display.get_default().get_default_seat().get_pointer()  # type: ignore
        _, x, y = pointer.get_position()  # type: ignore
        self.drag_start_x = x
        self.drag_start_y = y

        self.items._update()
        parent = self.btn.get_parent()  # type: ignore
        if parent:
            for child in parent.get_children():  # type: ignore
                if isinstance(child, Button):
                    child._wiggle.start()

        def _do_grab():
            if self.btn.get_realized():  # type: ignore
                self.btn.grab_add()  # type: ignore
                set_cursor_now(self.btn, "grab")
            return False

        GLib.idle_add(_do_grab)
        return False

    def make_btn(self, app_name: str, icon, indicator):
        self.app_name = app_name
        inner = Box(
            orientation="v",
            spacing=5,
            h_expand=False,
            v_expand=False,
            h_align="center",
            v_align="center",
        )
        inner.add(icon)
        if indicator:
            inner.add(indicator)
        self.btn = Button(name="dockstation-btn", tooltip_text=app_name, child=inner)
        self._wiggle = Wiggle(self.btn, self.dockstation.confh)
        self.btn._dockapp = self
        self.btn._wiggle = self._wiggle
        self.appcontextmenu = AppContextMenu(self.dockstation, self.app_name)
        self.buttonh = ButtonHandler(self)
        self.btn.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK  # type: ignore
            | Gdk.EventMask.BUTTON_RELEASE_MASK  # type: ignore
            | Gdk.EventMask.POINTER_MOTION_MASK  # type: ignore
            | Gdk.EventMask.ENTER_NOTIFY_MASK  # type: ignore
            | Gdk.EventMask.LEAVE_NOTIFY_MASK  # type: ignore
        )

        self.dockstation.main_event.connect(
            "leave-notify-event",
            lambda: self.buttonh._on_leave(widget=self.btn),  # type: ignore
        )
        self.btn.connect("button-press-event", self.buttonh.on_press)
        self.btn.connect("button-release-event", self.buttonh.on_release)
        self.btn.connect("enter-notify-event", self.dockstation.tools.hover_enter)
        self.btn.connect("motion-notify-event", self.buttonh.on_motion)
        self.appcontextmenu.menu.connect(
            "enter-notify-event", self.dockstation.tools.hover_enter
        )
        return self.btn
