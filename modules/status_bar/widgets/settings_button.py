from fabric.widgets.button import Button

from utils.widget_utils import setup_cursor_hover
from ...settings.start_menu import StartMenu


class SettingsButton(Button):
    def __init__(self):
        self.settings = StartMenu()
        super().__init__(
            label="⚙️",
            on_clicked=lambda *_: self.settings.utils.toggle("auto"),
        )
        setup_cursor_hover(self)
        self.settings.utils.toggle("hide")
