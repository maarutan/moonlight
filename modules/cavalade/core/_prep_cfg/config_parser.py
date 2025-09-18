from pathlib import Path
from config import CAVA_LOCAL_DIR
from utils import JsonManager, FileManager


class ConfParser:
    def __init__(
        self,
        config_name: str,
        config_file: str | Path,
    ) -> None:
        self.json = JsonManager()
        self.fm = FileManager()

        CAVA_LOCAL_DIR.mkdir(exist_ok=True, parents=True)
        self.local_config_file = CAVA_LOCAL_DIR / config_name

        self.file = config_file
        self.data = self.json.get_data(config_file)
        self.fm.write(self.local_config_file, self.to_ini())

    def to_ini(self) -> str:
        lines: list[str] = []
        for section, payload in self.data.items():
            lines.append(f"[{section}]")
            for key, value in payload.items():
                lines.append(f"{key} = {value}")
            lines.append("")
        return "\n".join(lines).strip()
