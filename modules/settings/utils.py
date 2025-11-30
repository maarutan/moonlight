from typing import TYPE_CHECKING, Literal, Optional
from fabric.utils import GLib, idle_add

if TYPE_CHECKING:
    from .start_menu import StartMenu


class Utils:
    def __init__(self, init_class: "StartMenu"):
        self.cfg = init_class
        self._hide_timeout_id: Optional[int] = None

        self.hide_class = "start-menu-hidden"
        self.show_class = "start-menu-show"

    def toggle(self, action: Literal["show", "hide", "auto"] = "auto"):
        from ..status_bar.bar import confh, widget_name

        if action == "auto":
            action = "hide" if self.cfg.is_hidden else "show"

        if action == "show" and not self.cfg.is_hidden:
            self.cfg.is_hidden = True
            self.cfg.margin = "100"
            self.cfg.add_style_class(self.show_class)

        if action == "hide" and self.cfg.is_hidden:
            self.cfg.is_hidden = False
            self.barpos = confh.get_option(f"{widget_name}.position", "top")

            match self.barpos:
                case "top":
                    self.cfg.margin = "-1200"
                case "left":
                    self.cfg.margin = "0 0 0 -1200"
                case "right":
                    self.cfg.margin = "0 -1200 0 0"
                case "bottom":
                    self.cfg.margin = "0 0 -1200 0"

            self.cfg.remove_style_class(self.show_class)
            self.cfg.add_style_class(self.hide_class)

    def _anchor(self) -> str:
        from ..status_bar.bar import confh, widget_name

        self.barpos = confh.get_option(f"{widget_name}.position", "top")

        match self.barpos:
            case "top":
                return "center top"
            case "left":
                return "top left"
            case "right":
                return "top right"
            case "bottom":
                return "center bottom"
            case _:
                return "center top"
