from time import sleep
from gi.repository import GLib
from pydbus import SessionBus
from threading import Thread


class ScreenCaptureMonitor:
    def __init__(self):
        self.bus = SessionBus()
        # правильный сервис и объект
        self.portal = self.bus.get(
            "org.freedesktop.portal.Desktop", "/org/freedesktop/portal/desktop"
        )
        self.is_capturing = False
        self.callbacks = []

        # Подписка на DBus-сигналы Screencast
        self.bus.subscribe(
            iface="org.freedesktop.portal.ScreenCast",
            signal="ScreencastStarted",
            object="/org/freedesktop/portal/desktop",
            signal_fired=self._handle_started,
        )

        self.bus.subscribe(
            iface="org.freedesktop.portal.ScreenCast",
            signal="ScreencastStopped",
            object="/org/freedesktop/portal/desktop",
            signal_fired=self._handle_stopped,
        )

        # GLib loop в отдельном потоке
        Thread(target=self._run_loop, daemon=True).start()

    def _run_loop(self):
        loop = GLib.MainLoop()
        loop.run()

    def _handle_started(self, *args):
        self.is_capturing = True
        for cb in self.callbacks:
            cb(True)

    def _handle_stopped(self, *args):
        self.is_capturing = False
        for cb in self.callbacks:
            cb(False)

    def subscribe(self, callback):
        self.callbacks.append(callback)


if __name__ == "__main__":
    while True:

        def on_capture(status):
            print("Экран записывается?", status)

        monitor = ScreenCaptureMonitor()
        monitor.subscribe(on_capture)
