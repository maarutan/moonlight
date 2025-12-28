from fabric.utils.helpers import Gtk
from shared.menu import Menu


def build_workspace_menu(conf, app_name: str, window: dict | None = None) -> Menu:
    ws_menu = Menu()
    for i in range(1, 11):
        it = Gtk.MenuItem(label=f"WS {i}")  # type: ignore
        if window is not None:
            it.connect(
                "activate",
                lambda *_, n=i, win=window: conf.actions.move_window_to_workspace(
                    win, n
                ),
            )
        else:
            it.connect(
                "activate", lambda *_, n=i: conf.actions.move_to_workspace(app_name, n)
            )
        ws_menu.append(it)
    ws_menu.show_all()
    return ws_menu
