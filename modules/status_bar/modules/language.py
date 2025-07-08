import subprocess, json
from fabric.hyprland.service import HyprlandEvent
from fabric.hyprland.widgets import Language, get_hyprland_connection
from fabric.widgets.label import Label
from fabric.widgets.button import Button


def get_keyboard_devices():
    try:
        out = subprocess.check_output(["hyprctl", "devices", "-j"])
        kb = json.loads(out).get("keyboards", [])
        return [d["name"] for d in kb]
    except Exception:
        return []


class LanguageBar(Button):
    def __init__(self):
        self._lang_label = Label(name="lang-label")
        super().__init__(
            name="language", h_align="center", v_align="center", child=self._lang_label
        )

        self.kb_devices = get_keyboard_devices()
        self.connect("clicked", self.on_clicked)

        self.connection = get_hyprland_connection()
        self.connection.connect("event::activelayout", self._on_language_switch)
        self._on_language_switch()

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
