from fabric.widgets.wayland import WaylandWindow as Window
from shared.windget_container import BaseWidget
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.box import Box


from .widgets.networkspeed import NetworkSpeedWidget
from .widgets.battery.battery import BatteryWidget
from .widgets.workspaces.workspaces import Workspaces
from .widgets.settings_button import SettingsButton
from .widgets.custom import CustomWidget
from .widgets.clock import ClockWidget
from .widgets.system_tray.systemtray import SystemTrayWidget
from .widgets.language import LanguageWidget
from .widgets.window_title import WindowTitleWidget
from .widgets.cava import CavaWidget

from functools import partial
from loguru import logger

from .config import StatusBarConfig

widget_name = "status-bar"
confh = StatusBarConfig(widget_name)
enabled = confh.get_option(f"{widget_name}.enabled", True)

if not enabled:
    StatusBar = None  # type: ignore
else:

    class StatusBar(Window, BaseWidget):
        widgets_registry: dict[str, type] = {
            "settings": SettingsButton,
            "workspaces": Workspaces,
            "battery": BatteryWidget,
            "network-speed": NetworkSpeedWidget,
            "clock": ClockWidget,
            "system-tray": SystemTrayWidget,
            "language": LanguageWidget,
            "window-title": WindowTitleWidget,
            "cava": CavaWidget,
        }

        def __init__(self):
            self.confh = confh
            self.widget_name = widget_name

            custom_section = self.confh.get_option(
                f"{self.widget_name}.widgets.custom", {}
            )
            for name in custom_section.keys():
                self.register_widget(
                    f"custom/{name}",
                    partial(CustomWidget, self, name),  # type: ignore
                )

            anchor = self._anchor_handler()
            layout = self._make_layout()
            orientation = "h" if self.is_horizontal() else "v"

            config = self._get_effective_config(orientation)

            container = CenterBox(
                name="status-bar-inner",
                orientation=orientation,
                start_children=Box(
                    orientation=orientation,
                    h_align="center",
                    v_align="center",
                    h_expand=True,
                    v_expand=True,
                    children=layout["start"],
                ),
                center_children=Box(
                    orientation=orientation,
                    h_align="center",
                    v_align="center",
                    h_expand=True,
                    v_expand=True,
                    children=layout["center"],
                ),
                end_children=Box(
                    orientation=orientation,
                    h_align="center",
                    v_align="center",
                    h_expand=True,
                    v_expand=True,
                    children=layout["end"],
                ),
            )

            style_props = {}
            if config.get("transparent", True):
                style_props["background"] = "transparent"
            rounded = config.get("rounded")
            if rounded and rounded != "0px":
                style_props["border-radius"] = rounded
            style = "; ".join(f"{k}: {v}" for k, v in style_props.items()) or None

            super().__init__(
                name=widget_name,
                anchor=anchor,
                child=container,
                exclusivity="auto",
                margin=config.get("margin", "0px 0px 0px 0px"),
                layer=config.get("layer", "top"),
                style=style,
            )
            self.show_all()

        def _get_effective_config(self, orientation: str) -> dict:
            base = {
                "margin": self.confh.get_option(
                    f"{widget_name}.margin", "0px 0px 0px 0px"
                ),
                "layer": self.confh.get_option(f"{widget_name}.layer", "top"),
                "transparent": self.confh.get_option(
                    f"{widget_name}.transparent", False
                ),
                "rounded": self.confh.get_option(f"{widget_name}.rounded", "0px"),
            }
            if orientation == "v":
                overrides = self.confh.get_option(f"{widget_name}.if-vertical", {})
                if overrides:
                    base.update(overrides)
            return base

        def _make_layout(self) -> dict:
            layout_config = self.confh.get_option(f"{widget_name}.widgets.layout", {})
            layout = {"start": [], "center": [], "end": []}

            for section, widgets in layout_config.items():
                if section not in layout:
                    logger.warning(
                        f"[{widget_name}] Unknown layout section '{section}'"
                    )
                    continue

                for name in widgets:
                    widget_cls = self.widgets_registry.get(name)
                    if widget_cls:
                        if isinstance(widget_cls, type):
                            layout[section].append(widget_cls(self))
                        else:
                            layout[section].append(widget_cls())
                    else:
                        logger.warning(
                            f"[{widget_name}] Unknown widget '{name}' in layout '{section}'"
                        )

            return layout

        def _anchor_handler(self) -> str:
            curr_pos = self.confh.get_option(f"{widget_name}.position", "top").lower()
            self._is_horizontal = curr_pos in ("top", "bottom")
            anchor_map = {
                "top": "left top right",
                "bottom": "left bottom right",
                "left": "top left bottom",
                "right": "top right bottom",
            }
            return anchor_map.get(curr_pos, "left top right")

        def is_horizontal(self) -> bool:
            return getattr(self, "_is_horizontal", True)

        @classmethod
        def register_widget(cls, name: str, widget_class: type):
            cls.widgets_registry[name] = widget_class

        @classmethod
        def _get_registry_widgets(cls) -> list[str]:
            return list(cls.widgets_registry.keys())
