import subprocess, json
from fabric.hyprland.service import HyprlandEvent
from fabric.hyprland.widgets import Language, get_hyprland_connection
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


class LanguageBar(Box):
    def __init__(self, orientation_pos: bool = True):
        self.orientation_pos = orientation_pos
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
            else Language().get_label()
        )
        self.set_tooltip_text(lang)
        self._lang_label.set_label(lang[:2].upper())
