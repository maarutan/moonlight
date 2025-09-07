from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._config_handler import ConfigHandlerStatusBar


class SystemTrayCfg:
    def __init__(
        self,
        cfg_handler: "ConfigHandlerStatusBar",
    ) -> None:
        self._cfg = cfg_handler
        self.parent = "system-tray"

    def icon_size(self) -> int:
        dflt = 1
        i = self._cfg._get_nested(self.parent, "icon-size", default=dflt)
        return i if isinstance(i, int) else dflt

    def refresh_interval(self) -> int:
        dflt = 1
        i = self._cfg._get_nested(self.parent, "refresh-interval", default=dflt)
        return i if isinstance(i, int) else dflt

    def spacing(self) -> int:
        dflt = 8
        i = self._cfg._get_nested(self.parent, "spacing", default=dflt)
        return i if isinstance(i, int) else dflt

    def tray_box(self) -> bool:
        dflt = False
        i = self._cfg._get_nested(self.parent, "tray-box", default=dflt)
        return i if isinstance(i, bool) else dflt

    def position_for_tray_box(self) -> str:
        position = self._cfg._get_options("position", "top")
        return position if isinstance(position, str) else "top"

    def box_position_handler(self) -> str:
        barpos = self.position_for_tray_box()

        start = self._cfg.modules.get_modules_start()
        center = self._cfg.modules.get_modules_center()
        end = self._cfg.modules.get_modules_end()

        if barpos == "top":
            if self.parent in start:
                return "top left"
            if self.parent in center:
                return "top"
            if self.parent in end:
                return "top right"

        elif barpos == "left":
            if self.parent in start:
                return "top left"
            if self.parent in center:
                return "center left"
            if self.parent in end:
                return "bottom left"

        elif barpos == "right":
            if self.parent in start:
                return "top right"
            if self.parent in center:
                return "center right"
            if self.parent in end:
                return "bottom right"

        elif barpos == "bottom":
            if self.parent in start:
                return "bottom left"
            if self.parent in center:
                return "bottom"
            if self.parent in end:
                return "bottom right"

        return "top"
