from typing import TYPE_CHECKING
from fabric.widgets.box import Box
from fabric.widgets.svg import Svg
from fabric.utils import GLib

from shared.app_icon import AppIcon

from .app_button import DockAppButton
from .indicator import WindowIndicator

if TYPE_CHECKING:
    from ..dock import DockStation


class DockStationItems(Box):
    def __init__(self, class_init: "DockStation"):
        self.conf = class_init
        super().__init__(
            name=self.conf.widget_name + "-items",
            orientation="h" if self.conf.tools.is_horizontal() else "v",
        )

        self.pinned = (
            self.conf.confh.get_option(f"{self.conf.widget_name}.pinned") or []
        )

        GLib.idle_add(self.build)
        events = ["openwindow", "closewindow"]
        for e in events:
            self.conf.hypr.hypr.connect(f"event::{e}", self.build)

    def build(self):
        for child in list(self.get_children()):
            self.remove(child)

        windows_counts = self.conf.hypr.windows_and_counts()
        all_apps = set(windows_counts.keys())

        self.set_spacing(5)
        for name, count in windows_counts.items():
            if count > 0:
                icon = AppIcon(name, icon_size=self.conf.config.get("icon-size"))
                indicator = WindowIndicator.get_svg(count)
                btn = DockAppButton(
                    conf=self.conf, app_name=name, icon=icon, indicator=indicator
                )
                self.add(btn)

        if any(count > 0 for count in windows_counts.values()):
            is_horizontal = self.conf.tools.is_horizontal()

            line = Box(name=self.conf.widget_name + "-line")

            if is_horizontal:
                line.add_style_class(self.conf.widget_name + "-line-vertical")

            self.add(line)

        for app in self.pinned:
            if app not in all_apps or windows_counts.get(app, 0) == 0:
                icon = AppIcon(app, icon_size=self.conf.config.get("icon-size"))
                indicator = WindowIndicator.get_svg(0)
                btn = DockAppButton(
                    conf=self.conf, app_name=app, icon=icon, indicator=indicator
                )
                self.add(btn)
