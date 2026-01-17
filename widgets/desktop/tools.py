from typing import Literal

from .core.widgetparent.parent import DesktopWidget


class DesktopTools:
    def __init__(self, desktop):
        self.desktop = desktop

    def toggle_edit_mode(self, action: Literal["show", "hide", "auto"] = "auto"):
        self.desktop.edit_mode = not self.desktop.edit_mode
        if action == "auto":
            action = "show" if self.desktop.edit_mode else "hide"

        if action == "show":
            self.desktop.edit_mode = True
        elif action == "hide":
            self.desktop.edit_mode = False

        if self.desktop.edit_mode:
            self.desktop.grid_overlay.show()
            for w in self.desktop.root.get_children():  # type: ignore
                if isinstance(w, DesktopWidget):
                    w.show_border()
        else:
            self.desktop.grid_overlay.hide()
            for w in self.desktop.root.get_children():  # type: ignore
                if isinstance(w, DesktopWidget):
                    w.hide_border()
