from .prep_modules import init_modules
from ._config_handler import ConfigHandlerStatusBar

import gi
from loguru import logger
from dataclasses import dataclass

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # type: ignore
from fabric.widgets.box import Box


@dataclass
class Modules:
    modules: dict


class ModulesHandler(Modules):
    def __init__(self):
        self.cfg = ConfigHandlerStatusBar()

        self.modules_start = self.cfg.modules.get_modules_start()
        self.modules_center = self.cfg.modules.get_modules_center()
        self.modules_end = self.cfg.modules.get_modules_end()

        built_modules = init_modules(cfg=self.cfg)

        super().__init__(modules=built_modules)
        self.__dict__.update(built_modules)

    def _modules_position_handler(self, position_keys: list[str]) -> list[Gtk.Widget]:
        widgets = []
        for key in position_keys:
            module = self.modules.get(key)
            if module is None:
                logger.warning(f"[ModulesHandler] Module '{key}' not found in registry")
                continue
            if not isinstance(module, Gtk.Widget):
                logger.warning(f"[ModulesHandler] Module '{key}' is not a Gtk.Widget")
                continue
            widgets.append(module)
        return widgets

    def _build_box(self, name: str, keys: list[str]) -> Box:
        box = Box(
            name=name,
            orientation="h" if self.cfg.bar.is_horizontal() else "v",
            children=self._modules_position_handler(keys),
        )
        if self.cfg.bar.is_horizontal():
            box.add_style_class("statusbar-modules-horizontal")
            box.remove_style_class("statusbar-modules-vertical")
        else:
            box.add_style_class("statusbar-modules-vertical")
            box.remove_style_class("statusbar-modules-horizontal")

        return box

    def modules_start_handler(self) -> Box:
        return self._build_box("bar-modules-start", self.modules_start)

    def modules_center_handler(self) -> Box:
        return self._build_box("bar-modules-center", self.modules_center)

    def modules_end_handler(self) -> Box:
        return self._build_box("bar-modules-end", self.modules_end)
