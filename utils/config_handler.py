from utils import JsonManager
from utils import FileManager

import copy
from pathlib import Path
from typing import Any


class ConfigHandler:
    def __init__(
        self,
        config_dir: Path | str,
        config_file: Path | str,
        default_config: dict,
    ) -> None:
        self.json = JsonManager()
        self.fm = FileManager()
        self.fm.if_not_exists_create(Path(config_dir))
        self.path = Path(config_file)
        # ensure parent dir exists (extra safety)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        # keep original default structure (do not mutate the passed dict)
        self.cfg = copy.deepcopy(default_config or {})

        self.generate_default_config()

    def generate_default_config(self) -> None:
        try:
            existing = self.json.get_data(self.path)
            if not existing or not isinstance(existing, dict):
                raise ValueError("Config empty or not a dict")
        except Exception:
            # если битый JSON, пустой или не словарь → перезаписываем дефолтом
            self.json.write(self.path, copy.deepcopy(self.cfg))

    def _get_options(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        data = self.json.get_data(self.path)
        if not isinstance(data, dict):
            data = {}
            changed = True
        else:
            changed = False

        if key not in data:
            # use deepcopy to avoid shared mutables
            data[key] = copy.deepcopy(default)
            changed = True

        if changed:
            self.json.write(self.path, data)

        return data.get(key, default)

    def _get_nested(self, *keys: str, default: Any = None) -> Any:
        if not keys:
            return default

        data = self.json.get_data(self.path)
        if not isinstance(data, dict):
            data = {}
            changed = True
        else:
            changed = False

        current = data
        for i, key in enumerate(keys):
            is_last = i == len(keys) - 1

            if is_last:
                if not isinstance(current, dict):
                    # defensive: replace with dict if somehow not a dict
                    # (this shouldn't happen because we ensure parent keys are dicts)
                    current = {}
                    changed = True

                if key not in current:
                    current[key] = copy.deepcopy(default)
                    changed = True

                # commit if we changed the structure
                if changed:
                    self.json.write(self.path, data)

                return current.get(key, default)
            else:
                # ensure the intermediate node is a dict; if not — replace it
                if key not in current or not isinstance(current[key], dict):
                    current[key] = {}
                    changed = True
                current = current[key]

        # fallback (should not reach here)
        if changed:
            self.json.write(self.path, data)
        return default
