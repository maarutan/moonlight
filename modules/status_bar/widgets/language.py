from utils.jsonc import Jsonc
from fabric.hyprland.service import HyprlandEvent
from fabric.hyprland.widgets import get_hyprland_connection
from fabric.hyprland.widgets import HyprlandLanguage as HLanguage
from fabric.utils import exec_shell_command
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.button import Button

from fabric.utils.helpers import exec_shell_command_async
from utils.widget_utils import setup_cursor_hover, merge

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bar import StatusBar


class LanguageWidget(Box):
    def __init__(
        self,
        init_class: "StatusBar",
    ) -> None:
        self.conf = init_class

        super().__init__(
            orientation="h" if self.conf.is_horizontal() else "v",
            name="sb_language",
        )

        config = self.conf.confh.get_option(
            f"{self.conf.widget_name}.widgets.language", {}
        )

        if not self.conf.is_horizontal():
            config = merge(config, config.get("if-vertical", {}))

        self.number_letters = config.get("number-letters", 2)
        self.register = config.get("register", "lower")
        self._lang_label = Label(name="sb_language-label")

        self.button = Button(
            name="sb_language-button",
            child=self._lang_label,
            on_clicked=self.on_clicked,
        )
        setup_cursor_hover(self.button, "pointer")
        self.children = [self.button]

        self.kb_devices = self.get_keyboard_devices()
        self.hlanguage = HLanguage()

        self._on_language_switch()
        self.connection = get_hyprland_connection()
        self.connection.connect("event::activelayout", self._on_language_switch)

    def get_keyboard_devices(self):
        try:
            out = exec_shell_command("hyprctl devices -j")
            kb = Jsonc.loads(f"{out}").get("keyboards", [])
            return [d["name"] for d in kb]
        except Exception:
            return []

    def on_clicked(self, *args):
        self._on_language_switch()
        for device in self.kb_devices:
            exec_shell_command_async(f"hyprctl switchxkblayout {device} next")

    def _on_language_switch(self, _=None, event: HyprlandEvent | None = None):
        lang = (
            event.data[1]
            if event and event.data and len(event.data) > 1
            else self.hlanguage.get_label()
        )
        self.set_tooltip_text(lang)
        short = lang[: self.number_letters]  # type: ignore
        self._lang_label.set_label(
            short.upper() if self.register in ["upper", "u"] else short.lower()
        )
