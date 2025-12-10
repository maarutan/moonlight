# app_window.py
from fabric.utils import GLib
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.scrolledwindow import ScrolledWindow
from fabric.widgets.revealer import Revealer
from fabric.widgets.box import Box
from modules.my_corner.corners import MyCorner
from .app_box import AppsBox
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .launcher import AppLauncher


class ALAppWindow(Box):
    def __init__(self, class_init: "AppLauncher"):
        self.conf = class_init
        super().__init__(
            name="al_window",
            exclusivity="none",
            orientation="v",
            h_align="end",
        )

        self.apps_box = AppsBox(self.conf)

        self.scrolled = ScrolledWindow(
            name="al_scrolled",
            h_align="fill",
            min_content_size=(480, 320),
            max_content_size=(480, 320),
            child=self.apps_box,
        )
        self.scrolled.remove_style_class("al_scrolled-bg-show")

        self.revealer = Revealer(
            child=self.scrolled,
            child_revealed=False,
            transition_type="slide-down",
            transition_duration=450,
        )

        self.l_cor = MyCorner(
            "top-left",
            corner_name="al_app-window-corner",
            corner_container_name="al_app-window-corner-con",
        )
        self.r_cor = MyCorner(
            "top-right",
            corner_name="al_app-window-corner",
            corner_container_name="al_app-window-corner-con",
        )

        self.l_cor.hide()
        self.r_cor.hide()

        self.add(
            CenterBox(
                start_children=self.r_cor,
                center_children=self.revealer,
                end_children=self.l_cor,
            )
        )

        self.conf.input.entry.connect("changed", self.on_changed)
        self.conf.input.entry.connect("activate", self.on_activate)

    def on_changed(self, e):
        text = e.get_text()
        self.apps_box.arrange_viewport(text)
        if text == "":
            self.revealer.unreveal()
            self.apps_box.hide()
            self.l_cor.hide()
            self.r_cor.hide()
            self.scrolled.remove_style_class("al_scrolled-bg-show")
        else:
            self.revealer.reveal()
            self.apps_box.show()
            self.l_cor.show()
            self.r_cor.show()
            self.scrolled.add_style_class("al_scrolled-bg-show")

    def on_activate(self, e):
        self.apps_box.launch_by_order(0)
        self.conf.tools.close()
        self.revealer.unreveal()
