import gi
import os
import signal

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk


class MyWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="GTK3 + сигнал")
        self.set_default_size(300, 150)

        # Box
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.box.set_homogeneous(False)
        self.box.set_margin_top(20)
        self.box.set_margin_bottom(20)
        self.box.set_margin_start(20)
        self.box.set_margin_end(20)
        self.add(self.box)

        # Label внутри Box
        self.label = Gtk.Label(label="Widget")
        self.label.set_name("widget_label")  # имя для CSS
        self.label.set_halign(Gtk.Align.CENTER)
        self.label.set_valign(Gtk.Align.CENTER)
        self.label.set_justify(Gtk.Justification.CENTER)

        # Оборачиваем Label в EventBox, чтобы CSS применялся к виджету
        self.event_box = Gtk.EventBox()
        self.event_box.add(self.label)
        self.event_box.set_name("widget_box")  # имя для CSS
        self.box.pack_start(self.event_box, True, True, 0)

        self.show_all()

        # CSS стили
        css = b"""
        #widget_box {
            background-color: #333333;
            border-radius: 15px;
            padding: 20px;
        }
        #widget_label {
            color: #ffffff;
            font-weight: bold;
            font-size: 16px;
        }
        """
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        # Системные сигналы через GLib
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGUSR1, self.hide_label)
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGUSR2, self.show_label)

    def hide_label(self):
        print("SIGUSR1: Скрываем Label")
        self.event_box.hide()
        return True  # ловим сигнал снова

    def show_label(self):
        print("SIGUSR2: Показываем Label")
        self.event_box.show()
        return True  # ловим сигнал снова


def main():
    win = MyWindow()
    win.connect("destroy", Gtk.main_quit)

    pid = os.getpid()
    print(f"PID этого процесса: {pid}")
    print("Используйте в другом терминале:")
    print(f"pkill -USR1 {pid}  # чтобы скрыть Label")
    print(f"pkill -USR2 {pid}  # чтобы показать Label")

    Gtk.main()


if __name__ == "__main__":
    main()
