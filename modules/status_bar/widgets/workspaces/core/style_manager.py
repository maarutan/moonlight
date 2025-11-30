from pathlib import Path
from typing import Any, Tuple

from loguru import logger
from utils.constants import Const
from utils.style_handler import StyleHandler
from utils.jsonc import Jsonc


class StyleManager:
    def __init__(self, cfg, base: str):
        self.cfg = cfg
        self.base = base

    def resolve(self) -> Tuple[Path, str]:
        style_opt = self.cfg.get_option(f"{self.base}.style", {"theme": "gnome"})
        current_dir = Path(Const.STATUS_BAR_CONFIG).parent
        base_dir = Const.CONFIG_STYLES_STATUSBAR_WORKSPACE / "workspaces"
        if isinstance(style_opt, dict):
            theme = (style_opt.get("theme") or "gnome").strip()
            if theme == "custom":
                cpath = style_opt.get("custom-style-path")
                if not cpath:
                    raise ValueError(
                        "[workspaces.style] 'custom-style-path' is required for custom theme"
                    )
                p = Path(str(cpath).format(current_dir=current_dir))
                return p, "custom"
            cand = base_dir / f"{theme}.jsonc"
            if not cand.exists():
                return base_dir / "gnome.jsonc", "gnome"
            return cand, theme
        if isinstance(style_opt, str):
            raw = style_opt.strip()
            if raw.startswith("{default}/"):
                name = Path(raw.replace("{default}/", "")).stem
                cand = base_dir / f"{name}.jsonc"
                if not cand.exists():
                    return base_dir / "gnome.jsonc", "gnome"
                return cand, name
            p = Path(str(raw).format(current_dir=current_dir))
            return p, (p.stem or "custom")
        return base_dir / "gnome.jsonc", "gnome"

    def apply(self) -> Tuple[str, Path, Any]:
        path, theme = self.resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            logger.warning(f"[workspaces.style] missing: {path} → fallback to gnome")
            path = (
                Const.CONFIG_STYLES_STATUSBAR_WORKSPACE / "workspaces" / "gnome.jsonc"
            )
            theme = "gnome"
        json_style = Jsonc.read(path)
        if not json_style:
            fb = Const.CONFIG_STYLES_STATUSBAR_WORKSPACE / "workspaces" / "gnome.jsonc"
            logger.warning(
                f"[workspaces.style] empty json: {path} → using fallback {fb}"
            )
            json_style = Jsonc.read(fb)
            theme = "gnome"
        handler = StyleHandler(json_style, path)
        scss_output = Path(Const.CURRENT_STYLE_STATUS_BAR_WORKSPACE)
        scss_output.parent.mkdir(parents=True, exist_ok=True)
        handler.save_scss(scss_output)
        return theme, path, json_style
