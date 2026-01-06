from math import cos, pi
from typing import TYPE_CHECKING
from fabric.utils import GLib, Gtk
from fabric.widgets.button import Button
from loguru import logger
from utils.widget_utils import set_cursor_now, setup_cursor_hover

if TYPE_CHECKING:
    from .app_button import DockAppButton

ANIM_FRAME_MS = 16
ANIM_DURATION_MS = 140
RAISE_PX = 12


class ButtonHandler:
    def __init__(self, dockapp: "DockAppButton"):
        self.dockapp = dockapp

    def _get_margin(self, widget, which: str) -> int:
        if which == "bottom":
            return widget.get_margin_bottom()
        if which == "top":
            return widget.get_margin_top()
        if which == "left":
            return widget.get_margin_left()
        if which == "right":
            return widget.get_margin_right()
        if which == "start":
            return widget.get_margin_start()
        if which == "end":
            return widget.get_margin_end()
        return 0

    def _set_margin(self, widget, which: str, value: int):
        if which == "bottom":
            widget.set_margin_bottom(value)
            return
        if which == "top":
            widget.set_margin_top(value)
            return
        if which == "left":
            widget.set_margin_left(value)
            return
        if which == "right":
            widget.set_margin_right(value)
            return
        if which == "start":
            widget.set_margin_start(value)
            return
        if which == "end":
            widget.set_margin_end(value)
            return

    def _is_vertical(self) -> bool:
        return bool(self.dockapp.dockstation.confh.is_vertical())

    def _animate_margin(
        self, widget, which: str, target: int, duration_ms: int = ANIM_DURATION_MS
    ):
        handle_name = f"_anim_handle_margin_{which}"
        handle = getattr(widget, handle_name, None)
        if handle:
            GLib.source_remove(handle)
            setattr(widget, handle_name, None)
        start = self._get_margin(widget, which)
        steps = max(1, int(duration_ms / ANIM_FRAME_MS))
        delta = target - start
        state = {"i": 0}

        def tick():
            state["i"] += 1
            t = state["i"] / steps
            eased = 0.5 * (1 - cos(pi * t))
            value = int(round(start + delta * eased))
            self._set_margin(widget, which, value)
            widget.queue_draw()
            if state["i"] >= steps:
                setattr(widget, handle_name, None)
                return False
            return True

        h = GLib.timeout_add(ANIM_FRAME_MS, tick)
        setattr(widget, handle_name, h)
        return h

    def _raise_icon(self, widget, px: int = RAISE_PX):
        anchor = self.dockapp.dockstation.confh.config["anchor"].lower()
        if self._is_vertical():
            if "right" in anchor:
                self._animate_margin(widget, "end", px)
            else:
                self._animate_margin(widget, "start", px)
        else:
            if "bottom" in anchor:
                self._animate_margin(widget, "bottom", px)
            else:
                self._animate_margin(widget, "top", px)

    def _lower_icon(self, widget):
        anchor = self.dockapp.dockstation.confh.config["anchor"].lower()
        if self._is_vertical():
            if "right" in anchor:
                self._animate_margin(widget, "end", 0)
            else:
                self._animate_margin(widget, "start", 0)
        else:
            if "bottom" in anchor:
                self._animate_margin(widget, "bottom", 0)
            else:
                self._animate_margin(widget, "top", 0)

    def on_press(self, widget, event):
        if not widget.get_realized():
            return False
        if event.button == 3:
            dock = widget._dockapp
            if dock and dock.appcontextmenu:
                dock.appcontextmenu.menu.popup(widget)
            return True
        if event.button == 1:
            dock = widget._dockapp
            dock._long_press_triggered = False
            dock.appcontextmenu.menu.popdown()

            if dock._long_press_handle:
                GLib.source_remove(dock._long_press_handle)
            setup_cursor_hover(dock.btn, "pointer")

            dock._long_press_handle = GLib.timeout_add(
                350, dock._on_long_press_triggered
            )

            dock._selected = True
            dock.btn.set_state_flags(Gtk.StateFlags.NORMAL, clear=True)
            widget._wiggle.stop()
            return True
        return False

    def on_release(self, widget, event):
        if not widget.get_realized():
            return False
        if event.button != 1:
            return False

        dock = widget._dockapp

        if dock._long_press_handle:
            GLib.source_remove(dock._long_press_handle)
            dock._long_press_handle = None

        if dock._dragging:
            dock._dragging = False
            dock._selected = False
            set_cursor_now(widget, "pointer")
            widget.grab_remove()
            self._lower_icon(widget)
            return True

        if not dock._long_press_triggered:
            dock.items.dockstation.actions.handle_app(
                dock.app_name,
                dock.items.dockstation.hypr.windows_for_app(dock.app_name),
            )

        dock._selected = False
        set_cursor_now(widget, "pointer")
        widget.grab_remove()
        self._lower_icon(widget)

        return True

    def on_motion(self, widget, event):
        if not widget.get_realized():
            return False

        dock = widget._dockapp
        if not dock or not dock._dragging:
            return False

        box = widget.get_parent()
        if not box:
            return True

        coords = widget.translate_coordinates(box, int(event.x), int(event.y))
        if not coords:
            return True

        mouse_x, mouse_y = coords
        horizontal = not dock.dockstation.confh.is_vertical()
        mouse_pos = mouse_x if horizontal else mouse_y
        children = box.get_children()
        new_index = 0

        for i, child in enumerate(children):
            if child is widget:
                continue
            alloc = child.get_allocation()
            start = alloc.x if horizontal else alloc.y
            length = alloc.width if horizontal else alloc.height
            center = start + length / 2.0
            if mouse_pos > center:
                new_index = i + 1 if i < children.index(widget) else i

        current_index = children.index(widget)
        if current_index != new_index:
            box.reorder_child(widget, new_index)
            dock.items.order = [
                child._dockapp.app_name
                for child in box.get_children()
                if isinstance(child, Button)
            ]

        return True

    def _on_leave(self, widget):
        dock = widget._dockapp
        parent = widget.get_parent()

        dock._dragging = False
        dock._selected = False
        if widget.get_realized():
            self._lower_icon(widget)

        if not parent:
            return
        for child in parent.get_children():
            if isinstance(child, Button):
                child._wiggle.stop()

        new_order = dock.items.get_current_order()

        dock.items.pinned = new_order

        if dock.dockstation.confh.config.get("widgets.dockstation.pinned") != new_order:
            dock.dockstation.confh.set_option("widgets.dockstation.pinned", new_order)

        dock.items._update(full_build=True)
