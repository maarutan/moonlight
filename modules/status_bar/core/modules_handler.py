import gi
from dataclasses import dataclass

from modules.status_bar.modules.clock import Clock
from .config_handler import ConfigHandler
from fabric.widgets.datetime import DateTime

from ..modules.logo import Logo
from ..modules.language import LanguageBar
from ..modules.workspace import WorkspacesBar
from ..modules.systemtray import SystemTrayBar
from ..modules.memory import Memory

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # type: ignore


@dataclass
class Modules:
    modules: dict


class ModulesHandler(Modules):
    def __init__(self):
        self.confh = ConfigHandler()

        self.modules_start = self.confh.get_modules_start()
        self.modules_center = self.confh.get_modules_center()
        self.modules_end = self.confh.get_modules_end()

        self.logo = Logo(
            orientation_pos=self.confh.is_horizontal(),
            content=self.confh.get_logo(),
            image_path=self.confh.get_logo_path(),
            type_=self.confh.get_logo_type(),
            image_size=self.confh.get_logo_size(),
        )

        self.clock = Clock(
            format=self.confh.get_clock(),
            orientation_pos=self.confh.is_horizontal(),
        )

        self.date_time = DateTime()
        self.workspaces = WorkspacesBar(
            workspaces_numbering=self.confh.get_workspaces_numbering(),
            orientation_pos=self.confh.is_horizontal(),
            maximum_value=self.confh.get_maximum_value(),
            magic_icon=self.confh.get_magic_icons(),
            enable_buttons_factory=self.confh.get_enable_buttons_factory(),
            enable_magic=self.confh.get_enable_magic(),
        )
        self.language = LanguageBar(orientation_pos=self.confh.is_horizontal())
        self.tray = SystemTrayBar(
            icon_size=self.confh.get_tray_icon_size(),
            refresh_interval=self.confh.get_tray_refresh_interval(),
            spacing=self.confh.get_tray_spacing(),
            orientation_pos=self.confh.is_horizontal(),
        )

        self.memory = Memory(
            icon=self.confh.get_memory_icon(),
            orientation_pos=self.confh.is_horizontal(),
            interval=self.confh.get_memory_interval(),
            format=self.confh.get_memory_format(),
        )
        super().__init__(
            modules={
                "logo": self.logo,
                "workspaces": self.workspaces,
                "language": self.language,
                "clock": self.clock,
                "tray": self.tray,
                "memory": self.memory,
            }
        )

    def _modules_position_handler(self, position_keys: list[str]) -> list:
        modules = []
        for key in position_keys:
            module = self.modules.get(key)
            if isinstance(module, Gtk.Widget):
                modules.append(module)
            else:
                print(f"[Config Warning] Module '{key}' is not a Gtk.Widget, skipping")
        return modules

    def modules_start_handler(self) -> list:
        return self._modules_position_handler(self.modules_start)

    def modules_center_handler(self) -> list:
        return self._modules_position_handler(self.modules_center)

    def modules_end_handler(self) -> list:
        return self._modules_position_handler(self.modules_end)
