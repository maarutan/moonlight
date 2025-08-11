from typing import Literal
from fabric.widgets.box import Box
from utils import FileManager
from .dashbord_popup import DashboardPopup
from .logo import Logo


class Profile(Box):
    def __init__(self, logo: dict, dashboard_profile_preview: dict, is_horizontal=True):
        self.popup_shown = False

        super().__init__(
            name="logo-container",
            orientation="h" if is_horizontal else "v",
        )

        self.fm = FileManager()
        self.popup = DashboardPopup(dashboard_profile_preview)

        self.logo = Logo(
            logo,
            on_click=self.do_clicked,
            popup_active=self.popup_shown,
        )
        self.add(self.logo)
        self.popup.connect("enter-notify-event", self._on_enter)
        self.popup.connect("leave-notify-event", self._on_leave)

        self.popup_toggle("hide")

    def popup_toggle(self, state: Literal["show", "hide"] = "show"):
        if state == "show":
            self.popup_shown = True
            self.logo.set_popup_active(True)

            self.popup.remove_style_class("statusbar-profile-popup-hide")
            self.popup.add_style_class("statusbar-profile-popup-show")
            self.popup.margin = "0"

        elif state == "hide":
            self.popup_shown = False
            self.logo.set_popup_active(False)

            self.popup.remove_style_class("statusbar-profile-popup-show")
            self.popup.add_style_class("statusbar-profile-popup-hide")
            self.popup.margin = "300 300 30 -900"

    def do_clicked(self, *args):
        if not self.popup_shown:
            self.popup_toggle("show")
        else:
            self.popup_toggle("hide")

    def _on_enter(self, *args):
        self.popup_toggle("show")

    def _on_leave(self, *args):
        self.popup_toggle("hide")
