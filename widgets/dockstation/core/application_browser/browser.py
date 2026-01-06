from fabric.widgets.svg import Svg
from fabric.widgets.box import Box
from fabric.widgets.button import Button
from fabric.widgets.flowbox import FlowBox
from fabric.widgets.scrolledwindow import ScrolledWindow
from fabric.utils import GLib, get_desktop_applications, DesktopApp
from fabric.widgets.label import Label

from .button_handler import ButtonHandler

from .search_icon import search_icon
from shared.animated_entry import Entry

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...dock import DockStation


class ApplicationBrowser(Box):
    def __init__(self, dockstation: "DockStation"):
        self.dockstation = dockstation
        self.SCROLL_SIZE = (800, 400)

        super().__init__(
            name="dockstation-appbrowser",
            orientation="v",
            spacing=6,
            visible=True,
            all_visible=True,
        )

        # --- search entry ---
        self.search_entry = Entry(
            name="dockstation-appbrowser-entry",
            h_align="fill",
            h_expand=True,
            size=(400, 0),
        )
        self.search_entry.set_placeholder_text("Search...")

        self.search_timer = None
        self.current_search_query = ""

        self.search_entry.connect("changed", self.on_search_changed)

        self.add(
            Box(name="dockstation-line", style_classes="dockstation-appbrowser-line")
        )

        self.add(
            Box(
                name="dockstation-appbrowser-searchbox",
                orientation="h",
                h_expand=True,
                h_align="center",
                spacing=10,
                children=[
                    Svg(svg_string=search_icon, size=32),
                    self.search_entry,
                    Box(
                        spacing=2,
                        children=[
                            Label("Ctrl"),
                            Label("+"),
                            Label("I"),
                        ],
                    ),
                ],
            )
        )

        # --- FlowBox ---
        self.app_box = FlowBox(
            name="dockstation-appbrowser-flowbox",
            orientation="v" if self.dockstation.confh.is_vertical() else "h",
            spacing=5,
            row_spacing=10,
            column_spacing=10,
            h_expand=True,
            h_align="fill",
            v_align="start",
            v_expand=False,
            visible=True,
            all_visible=True,
        )

        self.app_box.set_filter_func(self._flowbox_filter)

        if self.dockstation.confh.is_vertical():

            def resize_scroll(widget, allocation):
                self.SCROLL_SIZE = (allocation.width, allocation.height)
                self.scroll.max_content_size = self.SCROLL_SIZE

        self.scroll = ScrolledWindow(
            name="dockstation-appbrowser-scrollwindow",
            h_scrollbar_policy="never",
            v_scrollbar_policy="automatic",
            size=self.SCROLL_SIZE,
            child=self.app_box,
        )
        self.scroll.max_content_size = self.SCROLL_SIZE

        if self.dockstation.confh.is_vertical():
            self.dockstation.main_box.connect("size-allocate", resize_scroll)  # type: ignore

        self.all_apps: list[DesktopApp] = get_desktop_applications() or []
        self.filtered_apps: list[DesktopApp] = []
        self.items: list[Button] = []
        self.selected_index: int = -1

        self.populate_all_apps()

        self.add(self.scroll)

    # --- создание кнопок один раз ---
    def populate_all_apps(self):
        self.items = []
        for index, app in enumerate(self.all_apps):
            handler = ButtonHandler(self, app, index)
            btn = handler.btn

            btn._app_data = app

            self.app_box.add(btn)
            btn.show()
            self.items.append(btn)

        self.app_box.show_all()

    def on_search_changed(self, widget):
        if self.search_timer:
            try:
                GLib.source_remove(self.search_timer)
            except Exception:
                pass
            self.search_timer = None

        self.search_timer = GLib.timeout_add(150, self._perform_filter)

    def _perform_filter(self):
        self.current_search_query = (
            (self.search_entry.get_text() or "").strip().casefold()
        )
        try:
            self.app_box.invalidate_filter()
        except Exception:
            self._fallback_manual_filter()
        self.search_timer = None
        return False

    def _flowbox_filter(self, flowbox_child):
        if not self.current_search_query:
            return True

        try:
            btn = flowbox_child.get_child()
        except Exception:
            btn = flowbox_child

        if not hasattr(btn, "_app_data"):
            return False

        app = btn._app_data

        parts = []
        for attr in ("display_name", "name", "generic_name", "executable"):
            val = getattr(app, attr, None)
            if val:
                parts.append(str(val))
        search_target = " ".join(parts).casefold()

        return self.current_search_query in search_target

    def _fallback_manual_filter(self):
        q = self.current_search_query
        for btn in self.items:
            app = getattr(btn, "_app_data", None)
            if app is None:
                btn.hide()
                continue

            parts = []
            for attr in ("display_name", "name", "generic_name", "executable"):
                val = getattr(app, attr, None)
                if val:
                    parts.append(str(val))
            search_target = " ".join(parts).casefold()

            if not q or q in search_target:
                btn.show()
            else:
                btn.hide()

    def filter(self, query: str):
        self.current_search_query = (query or "").strip().casefold()
        try:
            self.app_box.invalidate_filter()
        except Exception:
            self._fallback_manual_filter()
