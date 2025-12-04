import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from typing import Optional

from fabric.utils.helpers import get_desktop_applications, DesktopApp
from typing import List


def find_app_by_partial_name(
    query: str, include_hidden: bool = False
) -> List[DesktopApp]:
    q = query.casefold()
    found = []
    for app in get_desktop_applications(include_hidden):
        if (app.name and q in app.name.casefold()) or (
            app.display_name and q in app.display_name.casefold()
        ):
            found.append(app)
    return found


class AppIconWidget(Gtk.Box):
    """
    Виджет для отображения иконки и имени приложения по его имени или части имени.
    """

    def __init__(
        self, app_name: str, include_hidden: bool = False, icon_size: int = 48
    ):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        self.app_name = app_name
        self.include_hidden = include_hidden
        self.icon_size = icon_size

        # Найти приложение (берем первое совпадение)
        self.app: Optional[DesktopApp] = self._find_app()

        # Иконка
        if self.app:
            pixbuf = self.app.get_icon_pixbuf(self.icon_size)
            if pixbuf:
                img = Gtk.Image.new_from_pixbuf(pixbuf)
            else:
                img = Gtk.Image.new()  # пустая иконка
            self.pack_start(img, False, False, 0)

            # Текст с именем
            label_text = (
                f"{self.app.display_name or self.app.name}\n({self.app.window_class})"
            )
            label = Gtk.Label(label=label_text, xalign=0)
            self.pack_start(label, True, True, 0)
        else:
            label = Gtk.Label(
                label=f"Приложение '{self.app_name}' не найдено", xalign=0
            )
            self.pack_start(label, True, True, 0)

        self.show_all()

    def _find_app(self) -> Optional[DesktopApp]:
        """Ищем приложение по частичному совпадению имени."""
        matches = find_app_by_partial_name(self.app_name, self.include_hidden)
        return matches[0] if matches else None


class AppWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="AppIconWidget Example")
        self.set_default_size(400, 100)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(box)

        # Виджеты для разных приложений
        firefox_widget = AppIconWidget("firefox")
        terminal_widget = AppIconWidget("terminal")
        telegram = AppIconWidget("telegram")
        kitty = AppIconWidget("kitty")

        box.pack_start(telegram, False, False, 0)
        box.pack_start(firefox_widget, False, False, 0)
        box.pack_start(kitty, False, False, 0)


if __name__ == "__main__":
    win = AppWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
