from shared.input import Input
from shared.switch import Switch
from typing import TYPE_CHECKING
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from shared.combotext import ComboText
from fabric.widgets.eventbox import EventBox
from fabric.widgets.centerbox import CenterBox
from utils.json_type_schema import block_position
from ....expandable import Expandable
from .bar_config import BarConfig
from utils.jsonc import Jsonc


if TYPE_CHECKING:
    from ..settings import ApplicationConfig


class StatusBarConfig(Box):
    def __init__(self, init_class: "ApplicationConfig"):
        from ......status_bar.bar import confh, widget_name

        self.cfg = init_class
        self.bar_confh = confh
        self.bar_name = widget_name
        self.bar_config = BarConfig(self)
        self.jsonc = Jsonc

        super().__init__(
            name="application-config",
            h_align="fill",
            v_align="fill",
            h_expand=True,
            v_expand=True,
        )

        if_vertical = Expandable(
            name="if-vertical",
            widget=self.bar_config.make_section(is_vertical=True),
        )
        widgets = Box(
            name="sm_section-config-widgets",
            orientation="v",
            h_align="fill",
            v_align="fill",
            h_expand=True,
            v_expand=True,
            children=[],
        )

        main_box = Box(
            name="sm_section-config-container",
            orientation="v",
            h_align="fill",
            v_align="fill",
            h_expand=True,
            v_expand=True,
            children=[
                self.bar_config.make_section(is_vertical=False),
                if_vertical,
                widgets,
                self.bar_config.make_widget_section(),
            ],
        )

        self.add(main_box)
        self.show_all()
