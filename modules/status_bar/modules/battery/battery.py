# battery_widget.py
from pathlib import Path
from typing import Literal, Optional
import threading
from fabric.widgets.eventbox import EventBox
from fabric.widgets.svg import Svg
from .custom_icons import CustomIcons, DEFAULT_ICONS
from services import BatteryService
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from .icons import BatteryIcons
from gi.repository import GLib, Gdk  # type: ignore
from loguru import logger


class Battery(Box):
    def __init__(
        self,
        is_horizontal: bool = True,
        percentage_enable: bool = True,
        percentage_action_type: Literal["show", "hover"] = "show",
        percentage_position: Literal["left", "right"] = "right",
        icon_enable: bool = True,
        icons_type: str = "default",
        if_icon_not_found: str = "[bat]",
        custom_icons_file_path: Optional[str] = None,
        custom_icons: Optional[dict] = None,
    ):
        self.battery = BatteryService()
        self.system_theme = "dark"
        self.icons_type = icons_type
        self._is_horizontal = is_horizontal
        self.icon_enable = icon_enable
        self.if_icon_not_found = if_icon_not_found

        self.custom_icons_handler = CustomIcons(
            user_icons=custom_icons, file_path=custom_icons_file_path
        )

        self.percentage_enable = percentage_enable
        self.percentage_action_type = percentage_action_type
        self.percentage_position = percentage_position
        self._update_lock = threading.Lock()
        self._update_in_progress = False
        super().__init__(
            name="statusbar-battery",
            h_align="center",
            v_align="center",
            orientation="h" if self._is_horizontal else "v",
            h_expand=True,
            v_expand=True,
        )
        self._child_box = Box(
            h_expand=True,
            v_expand=True,
            h_align="center",
            v_align="center",
            orientation="h" if self._is_horizontal else "v",
        )
        self._attach_child_box_to_self()
        try:
            self.battery_icons = BatteryIcons(self.system_theme).ICONS or {}
        except Exception:
            logger.exception("Failed to build initial BatteryIcons")
            self.battery_icons = {}

        def _on_battery_signal(*args):
            self._start_background_update()

        try:
            if hasattr(self.battery, "changed") and hasattr(
                self.battery.changed, "connect"
            ):
                self.battery.changed.connect(_on_battery_signal)
            elif hasattr(self.battery, "connect"):
                self.battery.connect("changed", _on_battery_signal)
            else:
                logger.warning("BatteryService exposes no known connect API")
        except Exception:
            logger.exception("Error connecting to battery change signal")
        self._percent_label = Label(label="0%")
        if self.percentage_enable and self.percentage_action_type == "hover":
            self._percent_label.hide()
        self._icon_widget: Optional[object] = None
        self._start_background_update()

    def _start_background_update(self) -> None:
        if self._update_in_progress:
            return

        def worker():
            with self._update_lock:
                self._update_in_progress = True
                try:
                    try:
                        raw = self.battery.get_property("Percentage")
                        percent = int(raw) if raw is not None else 0
                    except Exception:
                        percent = 0
                    percent = max(0, min(100, percent))
                    try:
                        icons = BatteryIcons(self.system_theme).ICONS or {}
                    except Exception:
                        icons = self.battery_icons or {}
                    chosen_path = None
                    if icons:
                        if str(percent) in icons:
                            chosen_path = icons[str(percent)]
                        else:
                            numeric = sorted(
                                int(k) for k in icons.keys() if str(k).isdigit()
                            )
                            nearest = max(
                                (n for n in numeric if n <= percent), default=None
                            )
                            if nearest is not None:
                                chosen_path = icons.get(str(nearest))
                            else:
                                chosen_path = icons.get("?")
                    GLib.idle_add(
                        self._apply_update,
                        percent,
                        chosen_path,
                        priority=GLib.PRIORITY_DEFAULT,
                    )
                except Exception:
                    logger.exception("Background battery worker failed")
                finally:
                    self._update_in_progress = False

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def _is_svg_path(self, s: Optional[str]) -> bool:
        try:
            if not s:
                return False
            sp = str(s)
            if sp.lower().endswith(".svg"):
                return True
            p = Path(sp)
            return p.exists() and p.is_file() and sp.lower().endswith(".svg")
        except Exception:
            return False

    def _make_icon_widget(self, value: Optional[str] = None):
        try:
            if self._is_svg_path(value):
                return EventBox(
                    child=Svg(
                        svg_file=str(value), h_align="center", v_align="center", size=38
                    )
                )
        except Exception:
            logger.exception("svg -> widget failed, falling back to Label")
        return EventBox(
            child=Label(
                label=f" {value if self.icon_enable else self.if_icon_not_found} "
            )
        )

    def _apply_update(self, percent: int, chosen_path: Optional[str]) -> bool:
        try:
            percent = max(0, min(100, int(percent or 0)))
        except Exception:
            percent = 0
        self._clear_child_box()
        widget: Optional[object] = None
        if self.icon_enable:
            custom_keys = self.custom_icons_handler.dict_icon() or {}
            if self.icons_type == "default":
                if chosen_path:
                    widget = self._make_icon_widget(chosen_path)
                else:
                    widget = self._make_icon_widget()
            elif self.icons_type in custom_keys:
                try:
                    glyph = self.custom_icons_handler.icon_for_current(self.icons_type)
                except Exception:
                    glyph = ""
                if glyph:
                    widget = self._make_icon_widget(glyph)
                else:
                    widget = self._make_icon_widget()
            else:
                if chosen_path:
                    widget = self._make_icon_widget(chosen_path)
                else:
                    widget = self._make_icon_widget()
        else:
            widget = self._make_icon_widget()
        self._percent_label.set_text(f"{percent}%")
        if self.percentage_enable:
            if self.percentage_action_type == "hover":
                try:
                    self._percent_label.hide()
                except Exception:
                    pass
                self._safe_box_add(self._percent_label)
                self._attach_hover(widget)
                self._safe_box_add(widget)
            else:
                if self.percentage_position == "left":
                    self._safe_box_add(self._percent_label)
                    self._safe_box_add(widget)
                else:
                    self._safe_box_add(widget)
                    self._safe_box_add(self._percent_label)
        else:
            self._safe_box_add(widget)
        self._icon_widget = widget
        return False

    def _attach_hover(self, widget):
        if widget is None or not hasattr(widget, "connect"):
            return

        def on_enter(*a):
            try:
                self._percent_label.show()
            except Exception:
                pass
            return False

        def on_leave(*a):
            try:
                self._percent_label.hide()
            except Exception:
                pass
            return False

        try:
            widget.connect("enter-notify-event", on_enter)
            widget.connect("leave-notify-event", on_leave)
        except Exception:
            pass

    def _attach_child_box_to_self(self) -> None:
        try:
            if hasattr(self, "add"):
                self.add(self._child_box)
            elif hasattr(self, "append"):
                self.append(self._child_box)
            elif hasattr(self, "pack_start"):
                self.pack_start(self._child_box, True, True, 0)
            elif hasattr(self._child_box, "set_parent"):
                self._child_box.set_parent(self)
            else:
                setattr(self, "_child_box_attached", self._child_box)
        except Exception:
            logger.exception("Failed to attach _child_box to parent container")

    def _clear_child_box(self) -> None:
        try:
            if hasattr(self._child_box, "remove_all"):
                self._child_box.remove_all()
                return
            if hasattr(self._child_box, "get_children") and hasattr(
                self._child_box, "remove"
            ):
                for child in list(self._child_box.get_children()):
                    try:
                        self._child_box.remove(child)
                    except Exception:
                        try:
                            child.unparent()
                        except Exception:
                            pass
        except Exception:
            logger.exception("Error while clearing _child_box")

    def _safe_box_add(self, widget) -> None:
        if widget is None:
            logger.debug("Skipping _safe_box_add because widget is None")
            return
        try:
            if hasattr(self._child_box, "add"):
                self._child_box.add(widget)
            elif hasattr(self._child_box, "append"):
                self._child_box.append(widget)
            elif hasattr(self._child_box, "pack_start"):
                self._child_box.pack_start(widget, True, True, 0)
            elif hasattr(self._child_box, "children"):
                self._child_box.children.append(widget)
            else:
                logger.warning("Unable to add widget to _child_box — unsupported API")
        except Exception:
            logger.exception("Failed to add widget to _child_box")
