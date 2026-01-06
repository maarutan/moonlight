from utils.jsonc import jsonc
from fabric.hyprland.service import HyprlandEvent
from fabric.hyprland.widgets import get_hyprland_connection
from fabric.hyprland.widgets import HyprlandLanguage as HLanguage
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.button import Button

from fabric.utils.helpers import exec_shell_command_async, exec_shell_command
from utils.widget_utils import setup_cursor_hover, merge

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bar import StatusBar


class LanguageWidget(Box):
    def __init__(
        self,
        statusbar: "StatusBar",
    ) -> None:
        self.confh = statusbar.confh

        super().__init__(
            orientation="v" if self.confh.is_vertical() else "h",
            name="statusbar-language",
        )

        config = self.confh.config_modules["language"]

        if self.confh.is_vertical():
            config = merge(config, config["if-vertical"])

        self.number_letters = config["number-letters"]
        self.register = config["register"]
        self.replace_map = config["replace"]

        self._lang_label = Label(name="statusbar-language-label")

        self.button = Button(
            name="statusbar-language-button",
            child=self._lang_label,
            on_clicked=self.on_clicked,
            h_expand=False,
            v_expand=False,
            v_align="center",
            h_align="center",
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
            kb = jsonc.loads(f"{out}").get("keyboards", [])
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

        lang = self.replace_map.get(lang, lang)

        self.set_tooltip_text(lang)
        short = lang[: self.number_letters]  # type: ignore
        self._lang_label.set_label(
            short.upper() if self.register in ["upper", "u"] else short.lower()
        )
