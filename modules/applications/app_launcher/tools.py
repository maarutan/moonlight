from typing import TYPE_CHECKING, Literal

from fabric.utils.helpers import GLib
from utils.events import event_close_popup, click_widget

if TYPE_CHECKING:
    from .launcher import AppLauncher


class ALTools:
    def __init__(self, class_init: "AppLauncher"):
        self.conf = class_init
        self.close_animation = None
        self.is_hidden = False
        self.hide_timeout = 200

    def close(self) -> None:
        self.toggle("hide")

        def close_widget():
            self.conf.shadow.toggle("hide")
            self.conf.hide()
            return False

        GLib.timeout_add(self.hide_timeout, close_widget)

    def events(self) -> None:
        self.conf.add_keybinding("Escape", self.close)
        event_close_popup(self.close, ignore_event="activewindow")
        click_widget(self.conf.shadow, self.close)

    def toggle(
        self,
        action: Literal[
            "show",
            "hide",
            "auto",
        ] = "auto",
    ) -> None:
        if action == "auto":
            action = "show" if self.is_hidden else "hide"

        self.conf.main_box.remove_style_class("popup-hide")
        self.conf.main_box.remove_style_class("popup-show")

        if action == "show":
            self.is_hidden = False
            self.conf.main_box.add_style_class("popup-show")
            self.conf.shadow.toggle("show")
            self.conf.show()

        elif action == "hide":
            self.is_hidden = True
            self.conf.main_box.add_style_class("popup-hide")
            self.conf.input.entry.set_text("")
            GLib.timeout_add(
                self.hide_timeout,
                lambda: (
                    self.conf.shadow.toggle("hide"),
                    self.conf.hide(),
                    False,
                ),
            )

    def _cancel_animation(self) -> bool:
        if self.close_animation:
            try:
                self.close_animation.cancel()
            except Exception:
                pass
            self.close_animation = None

        try:
            self.conf.hide()
        except Exception:
            pass

        return False

    def down(self) -> None:
        self.conf.app_window.apps_box.select_down()

    def up(self) -> None:
        self.conf.app_window.apps_box.select_up()
