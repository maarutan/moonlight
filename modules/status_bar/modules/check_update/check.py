import threading
from typing import Callable
from gi.repository import GLib  # type: ignore

from fabric.utils import exec_shell_command_async
from fabric.widgets.box import Box
from fabric.widgets.button import Button
from fabric.widgets.label import Label
from utils import setup_cursor_hover

from .distr import Arch, Debian, Fedora


class CheckUpdate(Box):
    def __init__(
        self,
        is_horizontal: bool = True,
        pkg_manager: str = "pacman",
        on_clicked: str = "notify-send 'Empty (statusbar - check-update)'",
        icon_position: str = "left",
        interval: int = 60,
    ):
        self.icon_position = icon_position

        super().__init__(
            name="statusbar-check-update",
            h_align="center",
            v_align="center",
        )

        icon: Callable[[str], Label] = lambda name: Label(
            name="statusbar-check-update-icon",
            label=name,
        )

        main_box = Box(
            name="statusbar-check-update-main-box",
            orientation="h" if is_horizontal else "v",
            h_align="center",
            v_align="center",
        )
        btn = Button(
            name="statusbar-check-update-btn",
            child=main_box,
            on_clicked=lambda *_: exec_shell_command_async(on_clicked),
        )
        setup_cursor_hover(btn, "pointer")
        self.add(btn)

        self.update_label = Label(label="…")

        for distr_cls in [Arch, Debian, Fedora]:
            distr = distr_cls()
            if distr.pkg_manager == pkg_manager:
                icon_widget = icon(getattr(distr, "icon", ""))
                if self.icon_position == "left":
                    main_box.add(icon_widget)
                    main_box.add(Label(" "))
                    main_box.add(self.update_label)
                else:
                    main_box.add(self.update_label)
                    main_box.add(Label(" "))
                    main_box.add(icon_widget)
                self.distr = distr
                break

        self.show_all()
        GLib.timeout_add_seconds(interval, self._update)

    def _update(self) -> bool:
        def worker():
            try:
                count = self.distr.quantity()
            except Exception:
                count = 0
            GLib.idle_add(self.update_label.set_label, str(count))

        threading.Thread(target=worker, daemon=True).start()
        return True
