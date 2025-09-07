from ...modules.workspaces.workspace import Workspaces
from .._config_handler import ConfigHandlerStatusBar


def workspaces_handler(cfg: ConfigHandlerStatusBar) -> Workspaces:
    return Workspaces(
        max_visible_workspaces=cfg.workspaces.max_visible_workspaces(),
        numbering_workpieces=cfg.workspaces.numbering_workpieces(),
        magic_icon=cfg.workspaces.magic_workspace()["icon"],
        magic_enable=cfg.workspaces.magic_workspace()["enable"],
        enable_buttons_factory=cfg.workspaces.enable_buttons_factory(),
        preview_image_size=cfg.workspaces.preview_workspace()["size"],
        preview_enable=cfg.workspaces.preview_workspace()["enable"],
        preview_event=cfg.workspaces.preview_workspace()["event"],
        preview_event_click=cfg.workspaces.preview_workspace()["event_click"],
        preview_anchor_handler=cfg.workspaces.preview_anchor_handler(),
        preview_missing_behavior=cfg.workspaces.preview_workspace()["missing-behavior"],
        # our bar is horizontal
        is_horizontal=cfg.bar.is_horizontal(),
    )
