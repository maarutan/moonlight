from typing import TYPE_CHECKING
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.svg import Svg
from utils.constants import Const
from .battery_svg_draw import BatteryHelper
from fabric.utils.helpers import idle_add
from fabric.widgets.eventbox import EventBox

if TYPE_CHECKING:
    from ...bar import StatusBar


class BatteryWidget(Box):
    def __init__(self, init_class: "StatusBar"):
        self.conf = init_class
        super().__init__(
            name="sb_battery",
            v_align="center",
            h_align="center",
            v_expand=True,
            h_expand=True,
            orientation="h" if self.conf.is_horizontal() else "v",
        )

        self.battery_helper = BatteryHelper()
        self.battery_cfg = f"{self.conf.widget_name}.widgets.battery"
        self.battery_cfg_dict = self.conf.confh.get_option(self.battery_cfg, {})

        idle_add(self.update)
        self.battery_helper.battery_service.changed.connect(self.update)

    def update(self):
        percent = int(
            self.battery_helper.battery_service.get_property("Percentage") or 0
        )

        battery_icon = Svg(
            svg_file=Const.BATTERY_ICON_SVG.as_posix(),
            size=35,
        )

        cfg = self.battery_cfg_dict.get("procentage", {}).copy()

        if not self.conf.is_horizontal():
            v_cfg = self.battery_cfg_dict.get("if-vertical", {}).get("procentage", {})
            cfg.update(v_cfg)

        enabled = cfg.get("enabled", True)
        position = cfg.get("position", "right")
        event_type = cfg.get("event", "hover")

        percentage_label = Label(f"{percent}%")

        if enabled:
            if position == "left":
                children = (
                    [percentage_label, Label(" "), battery_icon]
                    if self.conf.is_horizontal()
                    else [percentage_label, battery_icon]
                )
            else:
                children = [battery_icon, percentage_label]

            child_box = EventBox(
                child=Box(
                    orientation="h" if self.conf.is_horizontal() else "v",
                    children=children,
                )
            )
            self.children = child_box

            if event_type == "hover":
                percentage_label.hide()

                def on_enter(_widget, _event):
                    percentage_label.show()
                    percentage_label.set_text(f"{percent}%")

                def on_leave(_widget, _event):
                    percentage_label.hide()

                child_box.connect("enter-notify-event", on_enter)
                child_box.connect("leave-notify-event", on_leave)

            else:
                percentage_label.set_text(f"{percent}%")
        else:
            self.children = [battery_icon]
