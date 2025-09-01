# custom_icons.py
from pathlib import Path
from typing import Any, Dict, Optional
from copy import deepcopy
from utils import JsonManager
from services import BatteryService, DeviceState

DEFAULT_ICONS = {
    "forward": {
        "charging": {
            5: "󰢟",
            10: "󰢜",
            20: "󰂆",
            30: "󰂇",
            40: "󰂈",
            50: "󰢝",
            60: "󰂉",
            70: "󰢞",
            80: "󰂊",
            90: "󰂋",
            100: "󰂅",
        },
        "discharging": {
            10: "󰁺",
            20: "󰁻",
            30: "󰁼",
            40: "󰁽",
            50: "󰁾",
            60: "󰁿",
            70: "󰂀",
            80: "󰂁",
            90: "󰂂",
            100: "󰁹",
        },
    },
    "lay": {
        "charging": {
            0: "",
            100: "",
        },
        "discharging": {
            20: "",
            40: "",
            60: "",
            80: "",
            100: "",
        },
    },
}


class CustomIcons:
    def __init__(self, user_icons: Optional[Dict[str, Any]], file_path: Optional[str]):
        self.jsonc = JsonManager()
        self.battery = BatteryService()
        self.default_icons = DEFAULT_ICONS
        self.user_icons = deepcopy(user_icons) if user_icons else {}
        self.file_icons: Dict[str, Any] = {}
        if file_path:
            try:
                p = Path(file_path)
                if p.exists():
                    raw = self.jsonc.get_data(p)
                    if isinstance(raw, dict):
                        self.file_icons = deepcopy(raw)
            except Exception:
                self.file_icons = {}
        self._merged = self._build_merged()

    def _ensure_theme_state(self, d: Dict[str, Any], theme: str, state: str):
        if theme not in d or not isinstance(d[theme], dict):
            d[theme] = {}
        if state not in d[theme] or not isinstance(d[theme][state], dict):
            d[theme][state] = {}

    def _merge_into(self, base: Dict[str, Any], other: Dict[str, Any]):
        for theme, states in (other or {}).items():
            if not isinstance(states, dict):
                continue
            if theme not in base or not isinstance(base[theme], dict):
                base[theme] = {}
            for state, mapping in states.items():
                if not isinstance(mapping, dict):
                    continue
                if state not in base[theme] or not isinstance(base[theme][state], dict):
                    base[theme][state] = {}
                for key, icon in mapping.items():
                    try:
                        int_key = int(key)
                    except Exception:
                        try:
                            int_key = int(float(key))
                        except Exception:
                            continue
                    base[theme][state][int_key] = icon

    def _normalize_result(self, d: Dict[str, Any]) -> Dict[str, Any]:
        res: Dict[str, Any] = {}
        for theme, states in (d or {}).items():
            res[theme] = {}
            charging = {}
            discharging = {}
            if isinstance(states, dict):
                for state_name, mapping in states.items():
                    target = (
                        charging
                        if state_name.lower().startswith("charg")
                        else discharging
                        if state_name.lower().startswith("discharg")
                        else None
                    )
                    if target is None:
                        continue
                    if isinstance(mapping, dict):
                        for k, v in mapping.items():
                            try:
                                ik = int(k)
                            except Exception:
                                try:
                                    ik = int(float(k))
                                except Exception:
                                    continue
                            target[ik] = v
            res[theme]["charging"] = dict(sorted(charging.items()))
            res[theme]["discharging"] = dict(sorted(discharging.items()))
        return res

    def _build_merged(self) -> Dict[str, Any]:
        base = deepcopy(self.default_icons or {})
        self._merge_into(base, self.file_icons)
        self._merge_into(base, self.user_icons)
        normalized = self._normalize_result(base)
        for theme in normalized:
            if "charging" not in normalized[theme]:
                normalized[theme]["charging"] = {}
            if "discharging" not in normalized[theme]:
                normalized[theme]["discharging"] = {}
        return normalized

    def dict_icon(self) -> Dict[str, Any]:
        return deepcopy(self._merged)

    def _get_percentage(self) -> int:
        possible_keys = [
            "Percentage",
            "percentage",
            "Capacity",
            "capacity",
            "Charge",
            "charge",
            "percentage_remaining",
            "PercentageRemaining",
        ]
        for k in possible_keys:
            try:
                val = self.battery.get_property(k)
                if val is None:
                    continue
                return int(float(val))
            except Exception:
                continue
        try:
            val = self.battery.get_property("Percentage")
            return int(float(val or 0))
        except Exception:
            return 0

    def _get_state(self) -> str:
        try:
            battery_state = self.battery.get_property("State")
            return DeviceState.get(int(battery_state or 0), "UNKNOWN")
        except Exception:
            return "UNKNOWN"

    def icon_for_current(self, theme: str = "forward") -> str:
        icons = self._merged.get(theme) or {}
        state_name = self._get_state()
        percent = max(0, min(100, self._get_percentage()))
        if state_name == "CHARGING":
            mapping = icons.get("charging", {})
        elif state_name == "DISCHARGING":
            mapping = icons.get("discharging", {})
        elif state_name == "FULLY_CHARGED":
            mapping = icons.get("charging", {}) or icons.get("discharging", {})
            if 100 in mapping:
                return mapping[100]
        else:
            mapping = icons.get("discharging", {}) or icons.get("charging", {})
        if not mapping:
            return ""
        keys = sorted([int(k) for k in mapping.keys()])
        candidate = None
        for k in keys:
            if k <= percent:
                candidate = k
            else:
                break
        if candidate is None:
            candidate = keys[0]
        return mapping.get(candidate, "")
