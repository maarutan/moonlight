#!/usr/bin/env python3
from typing import Iterable, Callable
import gi, json, os

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


# ---------- CONFIG ----------
CONFIG_PATH = "config.json"
DEFAULT_CONFIG = {
    "layout": {
        "start": ["workspaces"],
        "center": [],
        "end": ["custom/pacman-updates", "settings", "custom/nvim"],
    }
}

ALL_WIDGETS = [
    "workspaces",
    "clock",
    "battery",
    "network",
    "custom/pacman-updates",
    "settings",
    "custom/nvim",
    "cpu",
    "ram",
]


# ---------- COMPONENT ----------
class ModuleSelector(Gtk.Box):
    """Один блок выбора и управления списком модулей (start/center/end)."""

    def __init__(self, name: str, available: Iterable[str], modules: list[str]):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.name = name
        self.available = list(available)
        self.modules = list(modules)
        self._handlers: list[Callable[[list[str]], None]] = []

        # Заголовок
        self.pack_start(Gtk.Label(label=f"[ {name} ]", xalign=0), False, False, 0)

        # Панель выбора
        bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.pack_start(bar, False, False, 0)

        self.select_btn = Gtk.Button(label="Select ▼")
        self.select_btn.connect("clicked", self._show_menu)
        bar.pack_start(self.select_btn, True, True, 0)

        add_btn = Gtk.Button(label="+")
        add_btn.connect("clicked", self._on_add)
        bar.pack_start(add_btn, False, False, 0)

        # Стек добавленных модулей
        self.stack = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        self.pack_start(self.stack, True, True, 0)

        for m in self.modules:
            self._add_row(m)

    def _show_menu(self, *_):
        menu = Gtk.Menu()
        for w in self.available:
            item = Gtk.MenuItem(label=w)
            item.connect("activate", self._select_widget, w)
            menu.append(item)
        menu.show_all()
        menu.popup(None, None, None, None, 0, Gtk.get_current_event_time())

    def _select_widget(self, _, name: str):
        self.select_btn.set_label(name)

    def _on_add(self, *_):
        name = self.select_btn.get_label()
        if not name or name == "Select ▼":
            return
        if name not in self.modules:
            self.modules.append(name)
            self._add_row(name)
            self._emit_changed()
        self.select_btn.set_label("Select ▼")

    def _add_row(self, name: str):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        row.pack_start(Gtk.Label(label=name, xalign=0), True, True, 0)
        rm = Gtk.Button(label="✕")
        rm.connect("clicked", lambda *_: self._remove(name, row))
        row.pack_start(rm, False, False, 0)
        self.stack.pack_start(row, False, False, 0)
        self.stack.show_all()

    def _remove(self, name: str, row: Gtk.Box):
        if name in self.modules:
            self.modules.remove(name)
        row.destroy()
        self._emit_changed()

    def connect_changed(self, cb: Callable[[list[str]], None]):
        self._handlers.append(cb)

    def _emit_changed(self):
        for cb in self._handlers:
            cb(self.modules)


# ---------- MAIN APP ----------
class LayoutEditor(Gtk.Window):
    def __init__(self):
        super().__init__(title="Layout Config Editor")
        self.set_default_size(400, 500)
        self.set_border_width(10)

        # Загрузка / создание конфига
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH) as f:
                self.config = json.load(f)
        else:
            self.config = DEFAULT_CONFIG

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)

        # 3 секции: start, center, end
        self.sections = {}
        for sec in ["start", "center", "end"]:
            selector = ModuleSelector(sec, ALL_WIDGETS, self.config["layout"][sec])
            frame = Gtk.Frame()
            frame.add(selector)
            vbox.pack_start(frame, True, True, 0)
            self.sections[sec] = selector

        # Кнопка сохранения
        save_btn = Gtk.Button(label="💾 Save Config")
        save_btn.connect("clicked", self._save_config)
        vbox.pack_start(save_btn, False, False, 0)

        self.show_all()

    def _save_config(self, *_):
        for sec, selector in self.sections.items():
            self.config["layout"][sec] = selector.modules
        with open(CONFIG_PATH, "w") as f:
            json.dump(self.config, f, indent=2)
        print("Config saved!")


if __name__ == "__main__":
    win = LayoutEditor()
    win.connect("destroy", Gtk.main_quit)
    Gtk.main()
