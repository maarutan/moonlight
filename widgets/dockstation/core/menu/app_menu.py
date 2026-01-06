from fabric.utils.helpers import Gtk
from shared.menu import Menu
from .workspace_menu import build_workspace_menu

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...dock import DockStation


def build_app_menu(dockstation: "DockStation", app_name: str) -> Menu:
    m = Menu()
    windows = dockstation.hypr.windows_for_app(app_name)

    for w in windows:
        ws_val = w.get("workspace")
        if isinstance(ws_val, dict):
            ws_val = ws_val.get("id", 1)
        else:
            ws_val = ws_val or 1

        from fabric.widgets.label import Label
        from shared.app_icon import AppIcon
        from fabric.widgets.box import Box as WBox

        win_label_box = WBox(
            orientation="h",
            children=[
                AppIcon(app_name=app_name, icon_size=25),
                Label(label=f" WS:{ws_val} | {app_name}"),
            ],
        )
        win_item = Gtk.MenuItem(child=win_label_box)  # type: ignore

        win_actions = Menu()

        focus_item = Gtk.MenuItem(label="Focus")  # type: ignore
        focus_item.connect(
            "activate", lambda *_, win=w: dockstation.actions.focus_window(win)
        )
        win_actions.append(focus_item)

        close_win = Gtk.MenuItem(label="Close window")  # type: ignore
        close_win.connect(
            "activate", lambda *_, win=w: dockstation.actions.close_window(win)
        )
        win_actions.append(close_win)

        toggle_float = Gtk.MenuItem(label="Toggle Floating")  # type: ignore
        toggle_float.connect(
            "activate",
            lambda *_, win=w: dockstation.actions.toggle_floating_window(win),
        )
        win_actions.append(toggle_float)

        fullscreen = Gtk.MenuItem(label="Fullscreen")  # type: ignore
        fullscreen.connect(
            "activate", lambda *_, win=w: dockstation.actions.fullscreen_window(win)
        )
        win_actions.append(fullscreen)

        # Move to workspace -> submenu
        move_menu = build_workspace_menu(dockstation, app_name, window=w)
        move_menu.show_all()

        move_item = Gtk.MenuItem(label="Move to Workspace")  # type: ignore
        move_item.set_submenu(move_menu)
        win_actions.append(move_item)

        win_actions.show_all()
        win_item.set_submenu(win_actions)

        m.append(win_item)

    m.append(Gtk.SeparatorMenuItem())  # type: ignore

    new_win = Gtk.MenuItem(label="New window")  # type: ignore
    new_win.connect("activate", lambda *_: dockstation.actions.handle_app(app_name, []))
    m.append(new_win)

    pin_label = "🚮 Unpin" if app_name in dockstation.items.pinned else "📌 Pin"
    pin_item = Gtk.MenuItem(label=pin_label)  # type: ignore
    pin_item.connect(
        "activate",
        lambda *_: [
            dockstation.actions.pin_unpin(app_name),
            pin_item.set_label(
                "🚮 Unpin" if app_name in dockstation.items.pinned else "📌 Pin"
            ),
        ],
    )
    m.append(pin_item)

    close_all_item = Gtk.MenuItem(label="🚪 Close All")  # type: ignore
    close_all_item.connect(
        "activate",
        lambda *_: [
            dockstation.actions.close_window(w)
            for w in dockstation.hypr.windows_for_app(app_name)
        ],
    )
    m.append(close_all_item)

    m.show_all()
    return m
