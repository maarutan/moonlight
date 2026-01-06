from typing import TYPE_CHECKING, Literal, Optional, Dict, Any, Tuple
from fabric.hyprland import Hyprland
from fabric.utils.helpers import GLib
from fabric.widgets.box import Box

from .modules.anchors import ANCH_DICT

if TYPE_CHECKING:
    from .dock import DockStation


class DockStationTools:
    def __init__(self, dockstation: "DockStation"):
        self.dockstation = dockstation
        self.is_hidden = True
        self._hide_timeout: Optional[int] = None
        self._hover_timeout: Optional[int] = None
        self.hypr = Hyprland()
        self.is_hover = False
        self.anchor_position_dict = ANCH_DICT

    def _cancel_hide(self):
        if self._hide_timeout:
            GLib.source_remove(self._hide_timeout)
            self._hide_timeout = None

    def _perform_hide(self):
        self.dockstation.main_box.hide()
        self._hide_timeout = None
        return False

    def toggle(self, action: Literal["show", "hide", "auto"] = "auto"):
        hide = "dockstation-hide"
        show = "dockstation-show"

        line_show = "dockstation-hover-line-show"
        line_hide = "dockstation-hover-line-hide"

        self.dockstation.main_box.remove_style_class(hide)
        self.dockstation.main_box.remove_style_class(show)
        self.dockstation.hover_line.remove_style_class(line_hide)
        self.dockstation.hover_line.remove_style_class(line_show)

        if action == "auto":
            action = "show" if self.is_hidden else "hide"

        if action == "show":
            self._cancel_hide()
            self.is_hidden = False

            self.dockstation.main_box.add_style_class(show)
            self.dockstation.hover_line.add_style_class(line_hide)
            self.dockstation.main_box.show()

        elif action == "hide":
            self.is_hidden = True

            self.dockstation.main_box.add_style_class(hide)
            self.dockstation.hover_line.add_style_class(line_show)

            self._cancel_hide()
            self._hide_timeout = GLib.timeout_add(300, self._perform_hide)

    def hover_enter(self, *args):
        self.toggle("show")
        return False

    def hover_leave(self, *args):
        self.toggle("hide")
        return False

    def _cancel_hover_hide(self):
        if self._hover_timeout:
            GLib.source_remove(self._hover_timeout)
            self._hover_timeout = None

    def _get_main_box_size(self) -> Tuple[int, int]:
        try:
            h = int(self.dockstation.main_box.get_allocated_height())
        except Exception:
            try:
                h = int(
                    getattr(self.dockstation.main_box, "get_height", lambda: None)()
                    or 0
                )
            except Exception:
                h = int(self.dockstation.config.get("size", 36))
        try:
            w = int(self.dockstation.main_box.get_allocated_width())
        except Exception:
            try:
                w = int(
                    getattr(self.dockstation.main_box, "get_width", lambda: None)() or 0
                )
            except Exception:
                w = int(self.dockstation.config.get("size", 36))
        return w or int(self.dockstation.config.get("size", 36)), h or int(
            self.dockstation.config.get("size", 36)
        )

    def _get_dock_rect(self, monitor_id: int) -> Tuple[int, int, int, int]:
        mons = self.dockstation.hypr.data_monitors()
        mon = mons.get(int(monitor_id)) if mons else None
        if not mon:
            mon = (
                next(iter(mons.values())) if mons else {"x": 0, "y": 0, "w": 0, "h": 0}
            )
        mx, my, mw, mh = (
            int(mon.get("x", 0)),
            int(mon.get("y", 0)),
            int(mon.get("w", 0)),
            int(mon.get("h", 0)),
        )
        anchor = self.dockstation.config.get("anchor", "bottom").lower()
        mb_w, mb_h = self._get_main_box_size()
        if "top" in anchor:
            return mx, my, mw, mb_h
        if "bottom" in anchor:
            return mx, my + mh - mb_h, mw, mb_h
        if "left" in anchor:
            return mx, my, mb_w, mh
        if "right" in anchor:
            return mx + mw - mb_w, my, mb_w, mh
        return mx, my + mh - mb_h, mw, mb_h

    def _rects_touch(
        self, a: Tuple[int, int, int, int], b: Tuple[int, int, int, int]
    ) -> bool:
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        a_left, a_top, a_right, a_bottom = ax, ay, ax + aw, ay + ah
        b_left, b_top, b_right, b_bottom = bx, by, bx + bw, by + bh
        if a_right < b_left or a_left > b_right or a_bottom < b_top or a_top > b_bottom:
            return False
        return True

    def _window_rect(self, w: Dict[str, Any]) -> Tuple[int, int, int, int]:
        at = w.get("at") or w.get("position") or [w.get("x", 0), w.get("y", 0)]
        size = (
            w.get("size")
            or w.get("resolution")
            or w.get("res")
            or [w.get("width", 0), w.get("height", 0)]
        )
        try:
            x = int(at[0])
            y = int(at[1])
        except Exception:
            x = int(w.get("x", 0) or 0)
            y = int(w.get("y", 0) or 0)
        try:
            w_w = int(size[0])
            w_h = int(size[1])
        except Exception:
            w_w = int(w.get("width", w.get("w", 0)) or 0)
            w_h = int(w.get("height", w.get("h", 0)) or 0)
        return x, y, w_w, w_h

    def _check_and_toggle(self):
        aw = self.dockstation.hypr.data_activewindow()
        if not aw:
            self.toggle("show")
            return
        win_rect = self._window_rect(aw)
        mon_id = int(aw.get("monitor", 0) or 0)
        dock_rect = self._get_dock_rect(mon_id)
        floating = bool(aw.get("floating", False))
        if not floating:
            self.toggle("hide")
            return
        if floating and not self._rects_touch(win_rect, dock_rect):
            self.toggle("show")
            return
        self.toggle("hide")

    def auto_hide(self) -> None:
        def check(*_):
            try:
                self._check_and_toggle()
            except Exception:
                if self.dockstation.hypr.data_activewindow() != {}:
                    self.toggle("hide")

                else:
                    self.toggle("show")

        events = [
            "activewindowv2",
            "changefloatingmode",
            "openwindow",
            "closewindow",
        ]
        for e in events:
            self.dockstation.hypr.hyprctl.connect(f"event::{e}", check)

        GLib.idle_add(check)

    def refresh(self):
        GLib.idle_add(self.dockstation.items.build)

    def toggle_pinned(self, box: Box, action: Literal["show", "hide"]):
        hide = "dock-station-pinned-hide"
        show = "dock-station-pinned-show"
        ctx = box.get_style_context()

        if action == "show":
            ctx.remove_class(hide)
            ctx.add_class(show)
        elif action == "hide":
            ctx.remove_class(show)
            ctx.add_class(hide)
