# ┌─┐┌┬┐┌─┐┌┬┐┬ ┬┌─┐  ┌┐ ┌─┐┬─┐
# └─┐ │ ├─┤ │ │ │└─┐  ├┴┐├─┤├┬┘
# └─┘ ┴ ┴ ┴ ┴ └─┘└─┘  └─┘┴ ┴┴└─
# --------------------------------------------------------------------------
# Copyright (c) 2025 maarutan. \ Marat Arzymatov All Rights Reserved.

from .core.module_handler import ModulesHandler
from .core._config_handler import ConfigHandler

from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.centerbox import CenterBox


class StatusBar(Window):
    def __init__(self, **kwargs):
        self.cfg = ConfigHandler()
        self.modules = ModulesHandler()
        self.bar_content = self._create_bar_content()

        super().__init__(
            visible=True,
            name="statusbar",
            all_visible=True,
            exclusivity="auto",
            child=self.bar_content,
            anchor=self.cfg.bar.position(),
            margin=self.cfg.bar.margin(),
            layer=self.cfg.bar.layer(),
            **kwargs,
        )

    def _create_bar_content(self) -> CenterBox:
        box = CenterBox(
            name="center-bar",
            orientation="h" if self.cfg.bar.is_horizontal() else "v",
        )
        box.start_children = self._get_start_children()
        box.center_children = self._get_center_children()
        box.end_children = self._get_end_children()
        return box

    def _get_start_children(self) -> list:
        return [self.modules.modules_start_handler()]

    def _get_center_children(self) -> list:
        return [self.modules.modules_center_handler()]

    def _get_end_children(self) -> list:
        return [self.modules.modules_end_handler()]
