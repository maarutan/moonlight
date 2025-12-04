from fabric.system_tray.widgets import SystemTray, SystemTrayItem
from fabric.widgets.grid import Grid
from fabric.utils.helpers import idle_add

from typing import TYPE_CHECKING, Dict, List, Optional
from utils.widget_utils import setup_cursor_hover

if TYPE_CHECKING:
    from ...bar import StatusBar


class SystemTrayItems(SystemTray):
    def __init__(
        self,
        class_init: "StatusBar",
        is_exist_popup: bool = False,
        columns: int = 4,
        icon_size: int = 32,
        **kwargs,
    ):
        self.conf = class_init
        self._icon_size = icon_size
        self.columns = columns
        self.is_exist_popup = is_exist_popup
        super().__init__(
            name="sb_system-tray-items",
            h_align="start",
            v_align="start",
            orientation="h" if self.conf.is_horizontal() else "v",
            **kwargs,
        )

        self.grid = Grid(
            name="sb_system-tray-grid-items",
            row_spacing=4,
            column_spacing=6,
        )
        super().add(self.grid)

        self._items: Dict[str, SystemTrayItem] = {}
        self._index = 0
        self._pending_add: List[str] = []
        self._idle_source_id: Optional[int] = None
        self._batch_size = 4

    def on_item_added(self, _, item_identifier: str):
        if item_identifier in self._items:
            return
        if item_identifier in self._pending_add:
            return
        self._pending_add.append(item_identifier)
        if self._idle_source_id is None:
            self._idle_source_id = idle_add(self._process_pending)

    def _process_pending(self):
        count = 0
        while self._pending_add and count < self._batch_size:
            item_id = self._pending_add[0]
            item = None
            watcher = getattr(self, "_watcher", None)
            if watcher:
                items = getattr(watcher, "items", None)
                if callable(items):
                    try:
                        items = items()
                    except Exception:
                        items = {}
                item = (items or {}).get(item_id)  # type: ignore

            if not item:
                break

            self._pending_add.pop(0)

            btn = SystemTrayItem(
                item=item,
                icon_size=self._icon_size,
            )
            setup_cursor_hover(btn)
            btn.add_style_class("sb_system-tray-items")

            if self.is_exist_popup:
                row = self._index // self.columns
                col = self._index % self.columns

                self.grid.attach(btn, col, row, 1, 1)
            else:
                super().add(btn)

            btn.show()
            self._items[item_id] = btn
            self._index += 1
            count += 1

        if self._pending_add:
            return True

        self._idle_source_id = None
        return False

    def on_item_removed(self, _, item_identifier: str):
        if item_identifier in self._pending_add:
            self._pending_add.remove(item_identifier)
            return

        btn = self._items.pop(item_identifier, None)
        if not btn:
            return

        try:
            if self.is_exist_popup:
                if hasattr(self.grid, "remove"):
                    self.grid.remove(btn)
                elif hasattr(self.grid, "detach"):
                    self.grid.detach(btn)  # type: ignore
            else:
                if hasattr(self, "remove"):
                    self.remove(btn)
        except Exception:
            pass

        try:
            btn.destroy()
        except Exception:
            btn.hide()
