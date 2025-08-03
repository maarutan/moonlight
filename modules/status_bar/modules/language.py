import subprocess, json
from typing import Literal
from fabric.hyprland.service import HyprlandEvent
from fabric.hyprland.widgets import get_hyprland_connection
from fabric.hyprland.widgets import Language as HLanguage
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from gi.repository import GLib, Gdk  # type: ignore


def get_keyboard_devices():
    try:
        out = subprocess.check_output(["hyprctl", "devices", "-j"])
        kb = json.loads(out).get("keyboards", [])
        return [d["name"] for d in kb]
    except Exception:
        return []


class Language(Box):
    def __init__(
        self,
        is_horizontal: bool = True,
        number_letters: int = 2,
        register: Literal["upper", "u", "lower", "l"] = "l",
    ):
        self.number_letters = number_letters
        self.register = register

        self.orientation_pos = is_horizontal
        self._lang_label = Label(name="lang-label")

        self.button = Button(
            child=self._lang_label,
            name="language-button",
            on_clicked=self.on_clicked,
        )

        super().__init__(
            orientation="h" if self.orientation_pos else "v",
            name="language",
            children=self.button,
        )

        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self._on_box_click)

        self.kb_devices = get_keyboard_devices()

        self.connection = get_hyprland_connection()
        self.connection.connect("event::activelayout", self._on_language_switch)

        self._on_language_switch()

    def _on_box_click(self, widget, event):
        self.button.emit("clicked")
        return True

    def on_clicked(self, *args):
        for device in self.kb_devices:
            subprocess.Popen(f"hyprctl switchxkblayout {device} next", shell=True)

    def _on_language_switch(self, _=None, event: HyprlandEvent = None):  # type: ignore
        lang = (
            event.data[1]
            if event and event.data and len(event.data) > 1
            else HLanguage().get_label()
        )
        self.set_tooltip_text(lang)

        self._lang_label.set_label(
            lang[: self.number_letters].upper()
            if self.register in ["upper", "u"]
            else lang[: self.number_letters].lower()
        )
