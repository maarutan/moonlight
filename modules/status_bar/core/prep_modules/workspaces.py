from ...modules.workspace import Workspaces
from .._config_handler import ConfigHandler


def workspaces_handler(cfg: ConfigHandler) -> Workspaces:
    return Workspaces(
        max_visible_workspaces=cfg.workspaces.max_visible_workspaces(),
        numbering_workpieces=cfg.workspaces.numbering_workpieces(),
        magic_icon=cfg.workspaces.magic_workspace()["icon"],
        magic_enable=cfg.workspaces.magic_workspace()["enable"],
        enable_buttons_factory=cfg.workspaces.enable_buttons_factory(),
        # our bar is horizontal
        is_horizontal=cfg.bar.is_horizontal(),
    )
