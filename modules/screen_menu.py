from gi.repository import Gdk, GLib  # type: ignore
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from utils.widget_utils import setup_cursor_hover


class Popup(Window):
    def __init__(self):
        super().__init__(
            name="popup-menu",
            exclusivity="auto",
            layer="top",
            anchor="none",
            style="background: rgba(0,0,0,0);",  # прозрачный фон
        )
        # содержимое меню
        self.box = Box(orientation="v")
        self.label = Label("hello world")
        self.box.add(self.label)
        # Можно добавить стили, паддинги и т.д.
        self.add(self.box)

    def show_at(self, x: int, y: int):
        # Если WaylandWindow поддерживает set_position или move
        try:
            self.move(x, y)
        except AttributeError:
            try:
                self.set_position(x, y)
            except AttributeError:
                pass
        self.show_all()


class ScreenMenu(Window):
    def __init__(self):
        super().__init__(
            name="screen-menu",
            exclusivity="auto",
            layer="bottom",
            anchor="top left bottom right",
            style="background: none;",
        )
        self.popup = Popup()
        self.popup.hide()

        # Левый клик по окну всего экрана
        self.connect("button-press-event", self._on_click)

    def _on_click(self, widget, event):
        if event.button == Gdk.BUTTON_PRIMARY:
            x = int(event.x_root)
            y = int(event.y_root)
            self.popup.show_at(x, y)
        return True
