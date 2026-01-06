from __future__ import annotations
import time
import re
from fabric.hyprland.service import Hyprland
from utils.jsonc import jsonc


class HyprState:
    HYPRCTL_CACHE_TTL = 0.1

    def __init__(self, hypr: Hyprland):
        self.hypr = hypr
        self._cache_ts: float = 0.0
        self._cache_data: dict = {}

    def _get_devices_json(self) -> dict:
        now = time.monotonic()
        if (now - self._cache_ts) < self.HYPRCTL_CACHE_TTL and self._cache_data:
            return self._cache_data
        reply = self.hypr.send_command("j/devices").reply
        raw = reply.decode("utf-8", errors="ignore")
        try:
            data = jsonc.loads(raw)
        except Exception:
            data = {}
        self._cache_data = data
        self._cache_ts = now
        return data

    def get_keyboard_info(self) -> dict:
        data = self._get_devices_json()
        try:
            return data["keyboards"][0]
        except Exception:
            return {}

    def get_layouts(self) -> list[str]:
        kb = self.get_keyboard_info()
        layout = kb.get("layout", [])
        if isinstance(layout, list):
            return [str(x) for x in layout]
        return [s for s in str(layout).split(",") if s]

    def get_active_keymap(self) -> str:
        kb = self.get_keyboard_info()
        return kb.get("active_keymap", "") or ""

    def norm(self, text: str | None) -> str:
        if not text:
            return ""
        return re.sub(r"\W", "", text).lower()

    def build_fullname_map(
        self, short_raw_list: list[str], default_fullnames: dict[str, str]
    ) -> dict[str, str]:
        kb = self.get_keyboard_info()
        short_norm = [self.norm(s) for s in short_raw_list]
        result: dict[str, str] = {}
        active_full = self.get_active_keymap()
        active_norm = self.norm(active_full)
        for idx, code in enumerate(short_norm):
            if code in default_fullnames:
                result[code] = default_fullnames[code]
                continue
            full_list = None
            for field in [
                "layout_names",
                "keymap_names",
                "variant_names",
                "options_names",
            ]:
                val = kb.get(field)
                if isinstance(val, list) and len(val) == len(short_norm):
                    full_list = val
                    break
            if full_list:
                result[code] = str(full_list[idx])
                continue
            if (
                code == active_norm
                or active_norm.startswith(code)
                or code in active_norm
            ):
                result[code] = active_full
                continue
            raw = short_raw_list[idx] if idx < len(short_raw_list) else code
            result[code] = raw.strip().replace("_", " ").title()
        return result
