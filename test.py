import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import time


class ClickDragWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Click or Drag GTK3")
        self.set_default_size(300, 200)

        self.button = Gtk.Button(label="Click or Drag")
        self.add(self.button)

        # Переменные состояния
        self.press_time = None
        self.dragging = False
        self.start_pos = None

        # Включаем обработку событий мыши
        self.button.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.BUTTON_RELEASE_MASK
            | Gdk.EventMask.POINTER_MOTION_MASK
        )

        # Подключаем события
        self.button.connect("button-press-event", self.on_button_press)
        self.button.connect("button-release-event", self.on_button_release)
        self.button.connect("motion-notify-event", self.on_motion)

    def on_button_press(self, widget, event):
        self.press_time = time.time()
        self.dragging = False
        self.start_pos = (event.x_root, event.y_root)
        return True  # перехватываем событие

    def on_motion(self, widget, event):
        if self.press_time is not None:
            dx = event.x_root - self.start_pos[0]
            dy = event.y_root - self.start_pos[1]
            if abs(dx) > 5 or abs(dy) > 5:  # порог для начала drag
                if not self.dragging:
                    print("Start dragging...")
                self.dragging = True
        return True

    def on_button_release(self, widget, event):
        if self.press_time is None:
            return True
        duration = time.time() - self.press_time
        if not self.dragging and duration < 0.5:  # короткий клик
            print("Button clicked!")
        elif self.dragging:
            print("Drag ended")
        self.press_time = None
        self.dragging = False
        return True


win = ClickDragWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
