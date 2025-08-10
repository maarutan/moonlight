import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib  # type: ignore

from fabric.widgets.box import Box
from utils import JsonManager
from config import STATUS_BAR_LOCK_MODULES


class PlayerProgressBar(Box):
    def __init__(
        self,
        player: str = "Unknown",
        media_value_length: tuple[float | int, float | int] = (0, 1),
    ):
        self.name = "progress-bar"

        super().__init__(
            name=self.name,
            orientation=Gtk.Orientation.VERTICAL,
            h_align="fill",
            v_align="fill",
        )

        self.json = JsonManager()
        self.status_bar_lock_modules = STATUS_BAR_LOCK_MODULES
        self.media_value_length = media_value_length

        self._progress = Gtk.ProgressBar(
            name="player-popup-progressbar",
            orientation=Gtk.Orientation.HORIZONTAL,
        )
        self._progress.set_show_text(True)
        self._progress.set_hexpand(True)

        progress_box = Box(
            name="player-popup-progress",
            orientation=Gtk.Orientation.VERTICAL,
            spacing=0,
            h_align="fill",
            v_align="center",
            all_visible=True,
            v_expand=False,
            children=self._progress,
        )
        self._progress_value = 0.0

        self.show_all()
        progress_box.show_all()
        self.children = [progress_box]
        self.__update()

        GLib.timeout_add_seconds(1, self.__update)

    def __format_time(self, us):
        seconds = int(us / 1000000)
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02}"

    def __update(self):
        pos, dur = self.media_value_length
        fraction = pos / dur if dur > 0 else 0.0

        self._progress_value = fraction
        self._progress.set_fraction(fraction)

        if pos != 0.0 and dur != 1.0:
            content = f"{self.__format_time(pos)} / {self.__format_time(dur)}"
            self.json.update(
                self.status_bar_lock_modules, "title_player.progress", content
            )
        else:
            content = (
                self.json.get_with_dot_data(
                    self.status_bar_lock_modules, "title_player.progress"
                )
                or "--:-- / --:--"
            )

        self._progress.set_text(content)
        return True
