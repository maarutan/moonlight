from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.svg import Svg
from utils.constants import Const
from .battery_svg_draw import BatteryHelper
from fabric.utils.helpers import idle_add


class BatteryWidget(Box):
    def __init__(self):
        super().__init__(
            name="sb_battery",
            v_align="center",
            h_align="center",
            v_expand=True,
            h_expand=True,
        )

        self.battery_helper = BatteryHelper()

        idle_add(self.update)
        self.battery_helper.battery_service.changed.connect(self.update)

    def update(self):
        battery_icon = Svg(
            svg_file=Const.BATTERY_ICON_SVG.as_posix(),
            size=35,
        )

        percent = self.battery_helper.battery_service.get_property("Percentage") or 0
        percent = int(percent)

        self.children = [
            battery_icon,
            Label(label=f"{round(percent, 0)}%"),
        ]
