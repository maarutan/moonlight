from functools import partial
from typing import TYPE_CHECKING, Callable, Dict

from fabric.widgets.box import Box
from loguru import logger

from ..modules.custom import CustomWidget
from .module_initialization import MODULES

if TYPE_CHECKING:
    from ..bar import StatusBar


class ModuleManager:
    def __init__(self, statusbar: "StatusBar"):
        self.statusbar = statusbar
        self.confh = statusbar.confh
        self.modules: Dict[str, Callable[["StatusBar"], object]] = {}

        # register built-in modules (wrap classes into factories that accept statusbar)
        for name, cls in MODULES.items():
            if isinstance(cls, type):
                self.modules[name] = (lambda C: (lambda sb: C(sb)))(cls)
            else:
                # if MODULES contains a factory already
                self.modules[name] = (lambda F: (lambda sb: F(sb)))(cls)

        # register custom modules from config (supports multiple config shapes)
        custom_section = {}
        # prefer confh.config_modules if available
        try:
            custom_section = (
                getattr(self.confh, "config_modules", {}).get("custom", {}) or {}
            )
        except Exception:
            custom_section = {}

        # fallback to get_option paths if necessary
        if not custom_section:
            try:
                widget_name = getattr(self.statusbar, "widget_name", "statusbar")
                maybe = getattr(self.confh, "get_option", None)
                if callable(maybe):
                    custom_section = maybe(f"{widget_name}.widgets.custom", {}) or {}
                    if not custom_section:
                        custom_section = (
                            maybe(f"{widget_name}.modules.custom", {}) or {}
                        )
            except Exception:
                custom_section = {}

        for name in custom_section.keys():  # type: ignore
            self.modules[f"custom/{name}"] = (
                lambda n: (lambda sb: CustomWidget(sb, n))
            )(name)

        self.layouts = self._make_layout()

    def _resolve_layout_config(self) -> dict:
        # Try multiple locations for layout configuration
        # 1) confh.config["layout"]
        try:
            cfg = getattr(self.confh, "config", None)
            if isinstance(cfg, dict) and "layout" in cfg:
                return cfg["layout"] or {}
        except Exception:
            pass

        # 2) confh.config_modules["statusbar"]["layout"] (older shapes)
        try:
            cms = getattr(self.confh, "config_modules", None)
            if isinstance(cms, dict):
                # try statusbar key if exists
                if "statusbar" in cms and isinstance(cms["statusbar"], dict):
                    return cms["statusbar"].get("layout", {}) or {}
        except Exception:
            pass

        # 3) confh.get_option("<widget>.widgets.layout") where widget name is on statusbar
        try:
            widget_name = getattr(self.statusbar, "widget_name", "statusbar")
            getter = getattr(self.confh, "get_option", None)
            if callable(getter):
                val = getter(f"{widget_name}.widgets.layout", {}) or getter(
                    f"{widget_name}.modules.layout", {}
                )
                if isinstance(val, dict):
                    return val
        except Exception:
            pass

        # 4) confh.get_option("layout")
        try:
            getter = getattr(self.confh, "get_option", None)
            if callable(getter):
                val = getter("layout", {}) or {}
                if isinstance(val, dict):
                    return val
        except Exception:
            pass

        return {}

    def _make_layout(self) -> dict:
        layout_config = self._resolve_layout_config()
        layout = {"start": [], "center": [], "end": []}

        for section, widget_names in layout_config.items():
            if section not in layout:
                logger.warning(f"Unknown layout section '{section}'")
                continue
            if not widget_names:
                continue
            for name in widget_names:
                factory = self.modules.get(name)
                if factory:
                    try:
                        layout[section].append(factory(self.statusbar))
                    except Exception as e:
                        logger.error(f"Failed to initialize widget '{name}': {e}")
                else:
                    logger.warning(f"Unknown widget '{name}' in layout '{section}'")
        return layout

    def _box_args(self) -> dict:
        return {
            "v_align": "center",
            "h_align": "center",
            "v_expand": True,
            "h_expand": True,
            "orientation": getattr(self.confh, "orientation", None)
            or getattr(self.confh, "config", {}).get("orientation", None),
        }

    def _make_box(self, children: list, name: str) -> Box:
        return Box(name=name, children=children, **self._box_args())

    def start_modules(self) -> Box:
        return self._make_box(self.layouts.get("start", []), "statusbar-modules-start")

    def center_modules(self) -> Box:
        return self._make_box(
            self.layouts.get("center", []), "statusbar-modules-center"
        )

    def end_modules(self) -> Box:
        return self._make_box(self.layouts.get("end", []), "statusbar-modules-end")
