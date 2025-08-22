from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._config_handler import ConfigHandler


class WorkspacesCfg:
    def __init__(self, cfg_handler: "ConfigHandler") -> None:
        self._cfg = cfg_handler
        self.parent = "workspaces"

    def max_visible_workspaces(self) -> int:
        dflt = 10
        i = self._cfg._get_nested(self.parent, "max-visible-workspaces", default=dflt)
        return i if isinstance(i, int) else dflt

    def numbering_workpieces(self) -> list[str]:
        dflt = [str(i) for i in range(1, 11)]
        i = self._cfg._get_nested(self.parent, "numbering-workpieces", default=dflt)
        return i if isinstance(i, list) else dflt

    def enable_buttons_factory(self) -> bool:
        dflt = True
        i = self._cfg._get_nested(self.parent, "enable-buttons-factory", default=dflt)
        return i if isinstance(i, bool) else dflt

    def magic_workspace(self) -> dict:
        dflt = {}
        i = self._cfg._get_nested(self.parent, "magic-workspace", default=dflt)
        return i if isinstance(i, dict) else dflt

    def preview_workspace(self) -> dict:
        dflt = {}
        i = self._cfg._get_nested(self.parent, "preview-workspace", default=dflt)
        return i if isinstance(i, dict) else dflt

    def preview_anchor_handler(self) -> str:
        dflt = "top left"
        position = self._cfg.bar.position()

        anchors = {
            "start": {
                "top": "top left",
                "bottom": "bottom left",
                "left": "top left",
                "right": "top right",
            },
            "center": {
                "top": "top center",
                "bottom": "bottom center",
                "left": "center left",
                "right": "center right",
            },
            "end": {
                "top": "top right",
                "bottom": "bottom right",
                "left": "bottom left",
                "right": "bottom right",
            },
        }

        module_groups = {
            "start": self._cfg.modules.get_modules_start(),
            "center": self._cfg.modules.get_modules_center(),
            "end": self._cfg.modules.get_modules_end(),
        }

        for group, modules in module_groups.items():
            if self.parent in modules:
                return anchors.get(group, {}).get(position, dflt)

        return dflt
