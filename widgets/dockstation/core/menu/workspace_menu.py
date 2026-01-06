from fabric.utils.helpers import Gtk
from shared.menu import Menu

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...dock import DockStation


def build_workspace_menu(
    conf: "DockStation", app_name: str, window: dict | None = None
) -> Menu:
    ws_menu = Menu()
    for i in range(1, 11):
        it = Gtk.MenuItem(label=f"WS {i}")  # type: ignore
        it.connect(
            "activate", lambda *_, n=i: conf.actions.move_to_workspace(app_name, n)
        )
        ws_menu.append(it)
    ws_menu.show_all()
    return ws_menu
