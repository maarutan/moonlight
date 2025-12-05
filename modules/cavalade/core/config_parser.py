from pathlib import Path
from typing import Any, Union
from utils.constants import Const
from utils.jsonc import Jsonc


def _ini_value(v: Any) -> str:
    if isinstance(v, bool):
        return "1" if v else "0"
    if v is None:
        return ""
    if isinstance(v, (list, dict)):
        return Jsonc.dumps(v)
    return str(v)


class ConfParser:
    def __init__(
        self,
        config_name: str,
        config_file: Union[str, Path, dict],
        section_path: str | None = None,
    ) -> None:
        self.local_config_file = Const.CAVA_LOCAL_DIR / f"{config_name}.ini"

        if isinstance(config_file, (str, Path)):
            data = Jsonc.get_data(config_file)
            if section_path:
                for part in section_path.split("."):
                    if not isinstance(data, dict):
                        data = {}
                        break
                    data = data.get(part, {})
        elif isinstance(config_file, dict):
            data = config_file
        else:
            raise TypeError("config_file must be a path or a dict")

        self.data = data if isinstance(data, dict) else {}

        self.local_config_file.parent.mkdir(parents=True, exist_ok=True)
        self.local_config_file.write_text(self.to_ini(), encoding="utf-8")

    def to_ini(self) -> str:
        lines: list[str] = []

        main_items = {k: v for k, v in self.data.items() if not isinstance(v, dict)}
        nested_sections = {k: v for k, v in self.data.items() if isinstance(v, dict)}

        if main_items:
            lines.append("[main]")
            for k, v in main_items.items():
                lines.append(f"{k} = {_ini_value(v)}")
            lines.append("")

        for section, payload in nested_sections.items():
            lines.append(f"[{section}]")
            for key, value in payload.items():
                lines.append(f"{key} = {_ini_value(value)}")
            lines.append("")

        return "\n".join(lines).strip()
