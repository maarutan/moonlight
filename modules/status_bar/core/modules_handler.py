from .config_handler import ConfigHandler
from ..modules.logo import Logo
from ..modules.language import LanguageBar
from ..modules.workspace import WorkspacesBar
from ..modules.systemtray import SystemTrayBar
from fabric.widgets.datetime import DateTime
from dataclasses import dataclass
import gi

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
            content=self.confh.get_logo(),
            image_path=self.confh.get_logo_path(),
            type_=self.confh.get_logo_type(),
        )

        self.date_time = DateTime()
        self.workspaces = WorkspacesBar(self.confh.get_workspaces_numbering())
        self.language = LanguageBar()
        self.tray = SystemTrayBar(
            icon_size=self.confh.get_tray_icon_size(),
            refresh_interval=self.confh.get_tray_refresh_interval(),
            spacing=self.confh.get_tray_spacing(),
        )

        super().__init__(
            modules={
                "logo": self.logo,
                "workspaces": self.workspaces,
                "language": self.language,
                "clock": self.date_time,
                "tray": self.tray,
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
        print(self._modules_position_handler(self.modules_start))
        return self._modules_position_handler(self.modules_start)

    def modules_center_handler(self) -> list:
        return self._modules_position_handler(self.modules_center)

    def modules_end_handler(self) -> list:
        return self._modules_position_handler(self.modules_end)
