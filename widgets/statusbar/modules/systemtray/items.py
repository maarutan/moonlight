from fabric.widgets.flowbox import FlowBox
from fabric.system_tray.widgets import SystemTray, SystemTrayItem
from typing import TYPE_CHECKING, Dict, Set
from utils.widget_utils import setup_cursor_hover
from fabric.utils import GLib
import threading
import time

if TYPE_CHECKING:
    from .systemtray import SystemTrayWidget


class SystemTrayItems(SystemTray):
    def __init__(self, systemtray: "SystemTrayWidget", **kwargs):
        self.systemtray = systemtray
        self._items: Dict[str, SystemTrayItem] = {}
        self._processing: Set[str] = set()
        self._cancelled: Set[str] = set()
        self._lock = threading.Lock()

        super().__init__(
            name="statusbar-system-tray-items",
            orientation="h",
            h_expand=True,
            h_align="fill",
            v_expand=False,
            v_align="start",
            **kwargs,
        )

        self.item_box = FlowBox(
            orientation="h",
            spacing=5,
            h_expand=True,
            h_align="fill",
            v_align="start",
            v_expand=False,
        )
        self.add(self.item_box)

    def on_item_added(self, _, item_identifier: str):
        with self._lock:
            if (
                item_identifier in self._items
                or item_identifier in self._processing
                or item_identifier in self._cancelled
            ):
                return
            self._processing.add(item_identifier)
        threading.Thread(
            target=self._process_and_add, args=(item_identifier,), daemon=True
        ).start()

    def _process_and_add(self, item_identifier: str):
        watcher = getattr(self, "_watcher", None)
        item = watcher.items.get(item_identifier) if watcher else None
        if not item:
            with self._lock:
                self._processing.discard(item_identifier)
            return

        with self._lock:
            if item_identifier in self._cancelled:
                self._processing.discard(item_identifier)
                return

        proxy = getattr(item, "_proxy", None)
        try:
            owner = proxy.get_name_owner() if proxy is not None else None
        except Exception:
            owner = None
        if not owner:
            with self._lock:
                self._processing.discard(item_identifier)
            return

        has_icon = False
        try:
            if getattr(item, "icon_name", None) or getattr(item, "icon_pixmap", None):
                has_icon = True
        except Exception:
            has_icon = False

        if not has_icon:
            for _ in range(5):
                time.sleep(0.08)
                with self._lock:
                    if item_identifier in self._cancelled:
                        self._processing.discard(item_identifier)
                        return
                try:
                    if getattr(item, "icon_name", None) or getattr(
                        item, "icon_pixmap", None
                    ):
                        has_icon = True
                        break
                except Exception:
                    continue

        if not has_icon:
            with self._lock:
                self._processing.discard(item_identifier)
            return

        with self._lock:
            if item_identifier in self._cancelled:
                self._processing.discard(item_identifier)
                return

        GLib.idle_add(self._add_widget_main, item_identifier, item)

    def _add_widget_main(self, item_identifier: str, item) -> bool:
        with self._lock:
            if item_identifier in self._items or item_identifier in self._cancelled:
                self._processing.discard(item_identifier)
                return False

        try:
            btn = SystemTrayItem(
                item=item, icon_size=self.systemtray.config["icon-size"]
            )
        except Exception:
            with self._lock:
                self._processing.discard(item_identifier)
            return False

        try:
            btn._identifier = item_identifier
        except Exception:
            pass

        setup_cursor_hover(btn)
        btn.add_style_class("statusbar-system-tray-items")
        self.item_box.add(btn)
        btn.show()

        with self._lock:
            self._items[item_identifier] = btn
            self._processing.discard(item_identifier)

        self.item_box.invalidate_sort()
        self.queue_draw()
        return False

    def on_item_removed(self, _, item_identifier):
        threading.Thread(
            target=self._process_item_remove, args=(item_identifier,), daemon=True
        ).start()

    def _process_item_remove(self, item_identifier: str):
        with self._lock:
            if item_identifier in self._processing:
                self._processing.discard(item_identifier)
            self._cancelled.add(item_identifier)
            btn = self._items.pop(item_identifier, None)

        if btn:
            GLib.idle_add(self._remove_widget_main, btn, item_identifier)
            return

        GLib.idle_add(self._remove_widget_by_identifier, item_identifier)

    def _remove_widget_main(self, btn, item_identifier: str) -> bool:
        try:
            self.item_box.remove(btn)
        except Exception:
            pass
        try:
            btn.destroy()
        except Exception:
            try:
                btn.hide()
            except Exception:
                pass

        with self._lock:
            self._cancelled.discard(item_identifier)

        self.item_box.invalidate_sort()
        self.queue_draw()
        return False

    def _remove_widget_by_identifier(self, item_identifier: str) -> bool:
        children = list(self.item_box.get_children())
        for child in children:
            try:
                ident = getattr(child, "_identifier", None)
                if ident == item_identifier:
                    try:
                        self.item_box.remove(child)
                    except Exception:
                        pass
                    try:
                        child.destroy()
                    except Exception:
                        try:
                            child.hide()
                        except Exception:
                            pass
                    break
            except Exception:
                continue
        with self._lock:
            self._cancelled.discard(item_identifier)
            self._processing.discard(item_identifier)
            self._items.pop(item_identifier, None)

        self.item_box.invalidate_sort()
        self.queue_draw()
        return False
