from typing import TYPE_CHECKING, Callable
from fabric.widgets.box import Box
from fabric.utils import GLib, Gdk
from fabric.widgets.button import Button
from fabric.widgets.eventbox import EventBox
from shared.app_icon import AppIcon
from .app_button import DockAppButton
from ..indicator import WindowIndicator
from utils.widget_utils import setup_cursor_hover
from .pinned_unpinned_anims import PinAnimator
from ..hamburger import HamburgerDrawing  # твой виджет
from utils.colors_parse import colors


if TYPE_CHECKING:
    from ...dock import DockStation


class DockStationItems(Box):
    def __init__(self, dockstation: "DockStation"):
        self.dockstation = dockstation
        super().__init__(
            name="dockstation-items",
            orientation=self.dockstation.confh.orientation,  # type: ignore
        )
        self.dockstation_application_browser_toggle = None
        self.hamburger = HamburgerDrawing()
        self.hamburger_event_box = EventBox(child=self.hamburger)
        self.hamburger_event_box.connect(
            "enter-notify-event",
            lambda: self.hamburger_event_box.set_style(
                f"background: {colors['surf0']}; border-radius: 0.5rem;"
            ),
        )
        self.hamburger_event_box.connect(
            "leave-notify-event",
            lambda: self.hamburger_event_box.set_style("background: none;"),
        )

        self.hamburger_widget = Box(
            name="dockstation-hamburger",
            children=self.hamburger_event_box,
        )

        self.pinned = self.dockstation.confh.config.get("pinned", [])
        self.pin_animator = PinAnimator(self)
        self.line_widget = None
        self.buttons: dict[str, Button] = {}
        self._dragging_mode = False

        events = ["openwindow", "closewindow"]
        for e in events:
            self.dockstation.hypr.hyprctl.connect(f"event::{e}", self._update)
        self._update(full_build=True)

    def _create_button(self, app_name: str, count: int, icon_size: int) -> Button:
        app_logic = DockAppButton(self)

        icon = AppIcon(app_name, icon_size=icon_size)
        indicator = WindowIndicator.get_svg(count)

        btn = app_logic.make_btn(
            app_name=app_name,
            icon=icon,
            indicator=indicator,
        )
        self.buttons[app_name] = btn
        setup_cursor_hover(btn)
        return btn

    def _ensure_button(self, app_name: str, count: int, icon_size: int) -> Button:
        btn = self.buttons.get(app_name)
        if not btn:
            btn = self._create_button(app_name, count, icon_size)
        return btn

    def _set_indicator(self, btn: Button, count: int):
        try:
            inner = btn.get_child()
            children = list(inner.get_children())  # type: ignore
            for c in children[1:]:
                inner.remove(c)  # type: ignore
            ind = WindowIndicator.get_svg(count)
            if ind is not None:
                inner.add(ind)  # type: ignore
                ind.show()
        except Exception:
            pass

    def _clear_container(self):
        for child in list(self.get_children()):
            self.remove(child)

    def _rebuild_default(self, windows_counts: dict, icon_size: int):
        self._clear_container()
        self.add(self.hamburger_widget)
        active = [name for name, c in windows_counts.items() if c > 0]
        for name in active:
            btn = self._ensure_button(name, windows_counts.get(name, 0), icon_size)
            if btn.get_parent() is None:
                self.add(btn)
            self._set_indicator(btn, windows_counts.get(name, 0))
            btn.set_visible(True)
        if active and self.pinned:
            if not self.line_widget:
                self.line_widget = Box(name="dockstation-line")

                if self.dockstation.confh.is_vertical():
                    self.line_widget.add_style_class("dockstation-line-vertical")

            if self.line_widget.get_parent() is None:
                self.add(self.line_widget)

            self.line_widget.set_visible(True)
        for p in self.pinned:
            if p not in active:
                btn = self._ensure_button(p, windows_counts.get(p, 0), icon_size)
                if btn.get_parent() is None:
                    self.add(btn)
                self._set_indicator(btn, windows_counts.get(p, 0))
                btn.set_visible(True)
        # hide any other buttons not in active/pinned
        shown = set(active) | set(self.pinned)
        for name, btn in list(self.buttons.items()):
            if name not in shown and btn.get_parent() is not None:
                try:
                    self.remove(btn)
                except Exception:
                    pass

    def _rebuild_dragging(self, windows_counts: dict, icon_size: int):
        self._clear_container()
        for p in self.pinned:
            btn = self._ensure_button(p, windows_counts.get(p, 0), icon_size)
            if btn.get_parent() is None:
                self.add(btn)
            self._set_indicator(btn, windows_counts.get(p, 0))
            btn.set_visible(True)
        # hide any other buttons not in pinned
        shown = set(self.pinned)
        for name, btn in list(self.buttons.items()):
            if name not in shown and btn.get_parent() is not None:
                try:
                    self.remove(btn)
                except Exception:
                    pass
        if self.line_widget:
            try:
                self.line_widget.set_visible(False)
            except Exception:
                pass

    def build(self):
        dragging = any(
            getattr(child, "_dockapp", None) and child._dockapp._dragging
            for child in self.get_children()
        )
        if dragging != self._dragging_mode:
            self._dragging_mode = dragging
            self._update(full_build=True)
        self.show_all()

    def _update(self, full_build=False):
        GLib.idle_add(self._update_idle, full_build)

    def _update_idle(self, full_build=False):
        windows_counts = self.dockstation.hypr.windows_and_counts()
        icon_size = self.dockstation.confh.config["icon-size"]
        dragging = any(
            getattr(child, "_dockapp", None) and child._dockapp._dragging
            for child in self.get_children()
        )
        if full_build or dragging != self._dragging_mode:
            self._dragging_mode = dragging
            if dragging:
                self._rebuild_dragging(windows_counts, icon_size)
            else:
                self._rebuild_default(windows_counts, icon_size)
            self.show_all()
            return
        # otherwise update indicators only
        for name, btn in self.buttons.items():
            count = windows_counts.get(name, 0)
            self._set_indicator(btn, count)
        if self.line_widget:
            self.line_widget.set_visible(
                not dragging
                and any(windows_counts.get(a, 0) > 0 for a in windows_counts)
            )
        self.show_all()

    def get_current_order(self) -> list[str]:
        order = []
        for child in self.get_children():
            if isinstance(child, Button) and hasattr(child, "_dockapp"):
                name = child._dockapp.app_name
                if name in self.pinned:  # только pinned
                    order.append(name)
        return order

    def _get_toggle(self, toggle: Callable):
        if toggle:
            self.hamburger.connect(
                "button-press-event",
                lambda widget, event: toggle(hamburger=self.hamburger),
            )
