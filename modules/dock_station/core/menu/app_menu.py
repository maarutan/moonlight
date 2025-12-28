from fabric.utils.helpers import Gtk
from shared.menu import Menu
from .workspace_menu import build_workspace_menu


def build_app_menu(conf, app_name: str) -> Menu:
    m = Menu()
    m.connect("deactivate", conf.tools.auto_hide)
    m.connect("selection-done", conf.tools.auto_hide)

    windows = conf.hypr.windows_for_app(app_name)

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
        focus_item.connect("activate", lambda *_, win=w: conf.actions.focus_window(win))
        win_actions.append(focus_item)

        close_win = Gtk.MenuItem(label="Close window")  # type: ignore
        close_win.connect("activate", lambda *_, win=w: conf.actions.close_window(win))
        win_actions.append(close_win)

        toggle_float = Gtk.MenuItem(label="Toggle Floating")  # type: ignore
        toggle_float.connect(
            "activate", lambda *_, win=w: conf.actions.toggle_floating_window(win)
        )
        win_actions.append(toggle_float)

        fullscreen = Gtk.MenuItem(label="Fullscreen")  # type: ignore
        fullscreen.connect(
            "activate", lambda *_, win=w: conf.actions.fullscreen_window(win)
        )
        win_actions.append(fullscreen)

        # Move to workspace -> submenu
        move_menu = build_workspace_menu(conf, app_name, window=w)
        move_menu.show_all()
        move_item = Gtk.MenuItem(label="Move to Workspace")  # type: ignore
        move_item.set_submenu(move_menu)
        win_actions.append(move_item)

        win_actions.show_all()
        win_item.set_submenu(win_actions)

        m.append(win_item)

    m.append(Gtk.SeparatorMenuItem())  # type: ignore

    new_win = Gtk.MenuItem(label="New window")  # type: ignore
    new_win.connect("activate", lambda *_: conf.actions.handle_app(app_name, []))
    m.append(new_win)

    pin_label = "🚮 Unpin" if app_name in conf.items.pinned else "📌 Pin"
    pin_item = Gtk.MenuItem(label=pin_label)  # type: ignore
    pin_item.connect("activate", lambda *_: conf.actions.pin_unpin(app_name))
    m.append(pin_item)

    close_all_item = Gtk.MenuItem(label="🚪 Close All")  # type: ignore
    close_all_item.connect(
        "activate",
        lambda *_: [
            conf.actions.close_window(w) for w in conf.hypr.windows_for_app(app_name)
        ],
    )
    m.append(close_all_item)

    m.show_all()
    return m
