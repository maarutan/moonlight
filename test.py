from config import BATTERY_ICONS
from utils import JsonManager
from services import BatteryService, DeviceState


class BatteryIcons:
    def __init__(self, system_theme="dark"):
        self.jsonc = JsonManager()
        self.battery = BatteryService()
        self.system_theme = system_theme
        self.svg_icons_dir = list(BATTERY_ICONS.iterdir())
        self.key = list(range(0, 101))
        self.dir_names = {
            "dark": ["battery_charging_dark", "battery_dark"],
            "light": ["battery_charging_light", "battery_light"],
        }
        self.icon_dir = self._collect_icons()
        self.ICONS = self.dict_icon()

    def _collect_icons(self):
        icons = []
        for theme_dir in self.svg_icons_dir:
            for d in self.dir_names.get(self.system_theme, []):
                if theme_dir.name == d:
                    icons.append(theme_dir)
        return icons

    def dict_icon(self):
        icons_dict = {}

        svg_dir = None
        if self.icon_dir:
            battery_state = self.battery.get_property("State")
            state = DeviceState.get(int(battery_state or 0), "UNKNOWN")

            if state == "CHARGING" and len(self.icon_dir) > 1:
                svg_dir = self.icon_dir[1]
            elif state == "DISCHARGING":
                svg_dir = self.icon_dir[0]
            else:
                svg_dir = self.icon_dir[0]

        if svg_dir:
            svg_files = {f.stem: f for f in svg_dir.glob("*.svg")}

            for k in self.key:
                k_str = str(k)
                if k_str in svg_files:
                    icons_dict[k_str] = str(svg_files[k_str])
                else:
                    nearest = max(
                        (
                            int(name)
                            for name in svg_files.keys()
                            if name.isdigit() and int(name) <= k
                        ),
                        default=None,
                    )
                    if nearest is not None:
                        icons_dict[k_str] = str(svg_files[str(nearest)])
                    else:
                        icons_dict[k_str] = str(svg_dir / "?.svg")

            icons_dict["?"] = str(svg_dir / "?.svg")
        else:
            icons_dict["?"] = None

        return icons_dict


if __name__ == "__main__":
    icons_dict = BatteryIcons().dict_icon()
    print(JsonManager().dumps(icons_dict, indent=2))
