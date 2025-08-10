import json
from typing import Literal
from fabric.hyprland.service import HyprlandEvent
from fabric.hyprland.widgets import get_hyprland_connection
from fabric.hyprland.widgets import Language as HLanguage
from fabric.utils import exec_shell_command
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.utils.helpers import exec_shell_command_async


class Language(Box):
    def __init__(
        self,
        is_horizontal: bool = True,
        number_letters: int = 2,
        register: Literal["upper", "u", "lower", "l"] = "l",
    ):
        super().__init__(
            orientation="h" if is_horizontal else "v",
            name="statusbar-language",
        )

        self.number_letters = number_letters
        self.register = register
        self._lang_label = Label(name="lang-label")

        self.button = Button(
            child=self._lang_label,
            name="statusbar-language-button",
            on_clicked=self.on_clicked,
        )
        self.children = [self.button]

        self.kb_devices = self.get_keyboard_devices()
        self.hlanguage = HLanguage()

        self._on_language_switch()
        self.connection = get_hyprland_connection()
        self.connection.connect("event::activelayout", self._on_language_switch)

    def get_keyboard_devices(self):
        try:
            out = exec_shell_command("hyprctl devices -j")
            kb = json.loads(f"{out}").get("keyboards", [])
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
        short = lang[: self.number_letters]
        self._lang_label.set_label(
            short.upper() if self.register in ["upper", "u"] else short.lower()
        )
