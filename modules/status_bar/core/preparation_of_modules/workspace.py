from ...modules.workspace import Workspaces
from .._config_handler import ConfigHandler


def workspace_handler(conf: ConfigHandler) -> Workspaces:
    return Workspaces(
        maximum_value=conf.get_maximum_value(),
        workspaces_numbering=conf.get_workspaces_numbering(),
        magic_icon=conf.get_magic_icons(),
        enable_magic=conf.get_enable_magic(),
        enable_buttons_factory=conf.get_enable_buttons_factory(),
        orientation_pos=conf.is_horizontal(),
    )
