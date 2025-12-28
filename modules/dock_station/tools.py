from typing import TYPE_CHECKING, Literal, Optional, Dict, Any, Tuple
from fabric.hyprland import Hyprland
from fabric.utils.helpers import GLib

from .modules.anchors import ANCH_DICT

if TYPE_CHECKING:
    from .dock import DockStation


class DockStationTools:
    def __init__(self, class_init: "DockStation"):
        self.conf = class_init
        self.is_hidden = True
        self._hide_timeout: Optional[int] = None
        self._hover_timeout: Optional[int] = None
        self.hypr = Hyprland()
        self.is_hover = False
        self.anchor_position_dict = ANCH_DICT

    def is_horizontal(self) -> bool:
        print(self._anchor_handler())
        return not self._anchor_handler() in ["left", "right"]

    def _anchor_handler(self) -> str:
        anchor_side = "bottom"  # дефолт
        anchor = self.conf.config.get("anchor", "")
        for key, value in self.anchor_position_dict.items():
            if anchor in value:
                anchor_side = key
                break
        return anchor_side

    def _cancel_hide(self):
        if self._hide_timeout:
            GLib.source_remove(self._hide_timeout)
            self._hide_timeout = None

    def _perform_hide(self):
        self.conf.main_box.hide()
        self._hide_timeout = None
        return False

    def toggle(self, action: Literal["show", "hide", "auto"] = "auto"):
        hide = f"{self.conf.widget_name}-hide"
        show = f"{self.conf.widget_name}-show"

        line_show = f"{self.conf.widget_name}-hover-line-show"
        line_hide = f"{self.conf.widget_name}-hover-line-hide"

        self.conf.main_box.remove_style_class(hide)
        self.conf.main_box.remove_style_class(show)
        self.conf.hover_line.remove_style_class(line_hide)
        self.conf.hover_line.remove_style_class(line_show)

        if action == "auto":
            action = "show" if self.is_hidden else "hide"

        if action == "show":
            self._cancel_hide()
            self.is_hidden = False

            self.conf.main_box.add_style_class(show)
            self.conf.hover_line.add_style_class(line_hide)
            self.conf.main_box.show()

        elif action == "hide":
            self.is_hidden = True

            self.conf.main_box.add_style_class(hide)
            self.conf.hover_line.add_style_class(line_show)

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
            h = int(self.conf.main_box.get_allocated_height())
        except Exception:
            try:
                h = int(getattr(self.conf.main_box, "get_height", lambda: None)() or 0)
            except Exception:
                h = int(self.conf.config.get("size", 36))
        try:
            w = int(self.conf.main_box.get_allocated_width())
        except Exception:
            try:
                w = int(getattr(self.conf.main_box, "get_width", lambda: None)() or 0)
            except Exception:
                w = int(self.conf.config.get("size", 36))
        return w or int(self.conf.config.get("size", 36)), h or int(
            self.conf.config.get("size", 36)
        )

    def _get_dock_rect(self, monitor_id: int) -> Tuple[int, int, int, int]:
        mons = self.conf.hypr.data_monitors()
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
        anchor = self.conf.config.get("anchor", "bottom").lower()
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
        aw = self.conf.hypr.data_activewindow()
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
                if self.conf.hypr.data_activewindow() != {}:
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
            self.conf.hypr.hypr.connect(f"event::{e}", check)

        GLib.idle_add(check)

    def refresh(self):
        GLib.idle_add(self.conf.items.build)
