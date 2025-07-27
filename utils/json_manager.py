import json
import re
from pathlib import Path
from typing import Any


class JsonManager:
    def _strip_comments(self, raw: str) -> str:
        import io

        output = io.StringIO()
        inside_str = False
        prev_char = ""

        for line in raw.splitlines():
            new_line = ""
            i = 0
            while i < len(line):
                char = line[i]

                if char == '"' and prev_char != "\\":
                    inside_str = not inside_str

                if (
                    not inside_str
                    and char == "/"
                    and i + 1 < len(line)
                    and line[i + 1] == "/"
                ):
                    break

                new_line += char
                prev_char = char
                i += 1

            output.write(new_line + "\n")

        return output.getvalue()

    def read(self, path: Path) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
            clean = self._strip_comments(raw)
            return json.loads(clean)

    def write(self, path: Path, data: dict, indent: int = 2) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent)

    def get_data(self, path: Path) -> dict:
        if path.exists():
            return self.read(path)
        return {}

    def update(self, path: Path, key: str, new_value: Any):
        data = self.get_data(path)
        keys = key.split(".")

        d = data
        for k in keys[:-1]:
            if k not in d or not isinstance(d[k], dict):
                d[k] = {}
            d = d[k]

        d[keys[-1]] = new_value
        self.write(path, data)

    def update_textually(self, path: Path, key: str, new_value: Any):
        val_pattern = r'(?:".*?"|\d+\.?\d*|true|false|null)'
        pattern = re.compile(
            rf'(["\']{re.escape(key)}["\']\s*:\s*){val_pattern}', re.IGNORECASE
        )
        text = path.read_text(encoding="utf-8")

        new_val = (
            f'"{new_value}"'
            if isinstance(new_value, str)
            else "null"
            if new_value is None
            else str(new_value).lower()
        )

        new_text, count = pattern.subn(rf"\1{new_val}", text)

        if count == 0:
            insert = f'  "{key}": {new_val},\n'
            new_text = re.sub(r"\}\s*$", insert + "}", new_text, count=1)

        path.write_text(new_text, encoding="utf-8")

    def append(self, path: Path, key: str, value: Any):
        data = self.get_data(path)
        keys = key.split(".")

        d = data
        for k in keys[:-1]:
            if k not in d or not isinstance(d[k], dict):
                d[k] = {}
            d = d[k]

        last_key = keys[-1]

        if last_key not in d or not isinstance(d[last_key], list):
            d[last_key] = []

        d[last_key].append(value)
        self.write(path, data)
