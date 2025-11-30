# utils/config_handler.py
from pathlib import Path
from typing import Any, Optional
from utils.constants import Const
from utils.jsonc import Jsonc, JsoncParseError
from loguru import logger


class ConfigHandler:
    def __init__(
        self,
        name: str,
        config_path: Path,
        default_config_path: Path,
        default_config: Optional[dict] = None,
        json_schema: Optional[dict] = None,
        debug: bool = False,
    ) -> None:
        self.name = name
        self.confp = config_path
        self.default_conf = default_config_path
        self.default_config = default_config or {}
        self.json_schema = json_schema or {}
        self.debug = debug

        self.json_schema_file_name = f"{self.name}-schema.json"
        self.json_schema_path = Const.JSON_SCHEMA_DIR / self.json_schema_file_name

        use_default_instead = False

        if self.confp.suffix not in [".json", ".jsonc"]:
            logger.warning(
                f"[{self.confp.name}] ❌ Invalid config format ({self.confp.suffix}). Using default config instead."
            )
            use_default_instead = True

        if self.default_conf.suffix not in [".json", ".jsonc"]:
            logger.error(
                f"[{self.default_conf.name}] ❌ Default config also has invalid format!"
            )
            raise ValueError("Both config and default config have invalid formats")

        self.default_conf.parent.mkdir(parents=True, exist_ok=True)
        self.default_conf.touch(exist_ok=True)
        if not self.default_conf.read_text(encoding="utf-8").strip():
            self.default_conf.write_text(
                Jsonc.dumps(self.default_config), encoding="utf-8"
            )

        if not use_default_instead:
            self.confp.parent.mkdir(parents=True, exist_ok=True)
            self.confp.touch(exist_ok=True)
            if not self.confp.read_text(encoding="utf-8").strip():
                self.confp.write_text(
                    Jsonc.dumps(self.default_config), encoding="utf-8"
                )

        self.target_path = self.default_conf if use_default_instead else self.confp

        if not self.json_schema_path.exists() and self.json_schema:
            self.json_schema_path.parent.mkdir(parents=True, exist_ok=True)
            self.json_schema_path.write_text(
                Jsonc.dumps(self.json_schema), encoding="utf-8"
            )

        try:
            self.config_data = Jsonc.get_data(self.target_path)
        except JsoncParseError as e:
            logger.opt(colors=True).error(e.pretty())
            raise SystemExit(
                f"[{self.name}] Configuration parsing failed. Fix the JSONC syntax and restart the app."
            )
        except Exception as e:
            logger.error(
                f"[{self.name}] Failed to load config ({self.target_path.name}): {e}"
            )
            self.config_data = Jsonc.get_data(self.default_conf)

        if self.name not in self.config_data:
            self.config_data[self.name] = self._copy_obj(
                self.default_config.get(self.name, {})
            )
            Jsonc.write(self.target_path, self.config_data)

        changed = self._deep_merge_defaults(
            self.config_data[self.name], self.default_config.get(self.name, {})
        )
        if changed:
            Jsonc.write(self.target_path, self.config_data)

        logger.debug(f"[{self.name}] Using config: {self.target_path}")

        if self.json_schema and self.config_data:
            schema_rule = self.json_schema.get(self.name)
            config_section = self.config_data.get(self.name)
            if schema_rule is not None and config_section is not None:
                self._validate_schema(config_section, schema_rule, self.name)

        if self.debug:
            logger.debug(Jsonc.dumps(self.config_data))

    def set_option(self, keypath: str, value: Any) -> None:
        try:
            Jsonc.update(self.target_path, keypath, value)
        except TypeError:
            Jsonc.append(self.target_path, keypath, value)

    def get_option(self, keypath: str, default: Optional[Any] = None) -> Any:
        try:
            value, found = Jsonc.get_path(self.target_path, keypath, default)
        except TypeError:
            value = Jsonc.get_path(self.target_path, keypath, default)
            found = value != default
        if not found:
            logger.warning(
                f"[{self.name}] Config option not found: {keypath}, using default: {default}"
            )
        return value

    def _validate_schema(self, data: Any, rule: Any, path: str = "") -> None:
        if not isinstance(rule, dict):
            return

        t_type = rule.get("type:type")
        t_enum = rule.get("type:enum")
        t_props = rule.get("type:properties")
        t_items = rule.get("type:items")
        t_required = rule.get("type:required", [])

        label = path or "<root>"

        if t_type is dict:
            if not isinstance(data, dict):
                logger.error(
                    f"[{self.name}] {label} → expected dict, got {type(data).__name__}"
                )
                return
        elif t_type is list:
            if not isinstance(data, list):
                logger.error(
                    f"[{self.name}] {label} → expected list, got {type(data).__name__}"
                )
                return
        elif t_type is not None:
            if not isinstance(data, t_type):
                logger.error(
                    f"[{self.name}] {label} → expected {t_type.__name__}, got {type(data).__name__}"
                )
                return

        if t_enum is not None and not isinstance(data, (dict, list)):
            if data not in t_enum:
                logger.error(
                    f"[{self.name}] {label} → invalid value '{data}', must be one of {t_enum}"
                )

        if t_props and isinstance(data, dict):
            if t_required:
                for req in t_required:
                    if req not in data:
                        logger.error(
                            f"[{self.name}] {label}.{req} → missing required key"
                        )
            for prop_name, prop_rule in t_props.items():
                if prop_name in data:
                    self._validate_schema(
                        data[prop_name], prop_rule, f"{label}.{prop_name}"
                    )

        if t_items and isinstance(data, list):
            for i, item in enumerate(data):
                self._validate_schema(item, t_items, f"{label}[{i}]")

    def _deep_merge_defaults(self, target: Any, defaults: Any) -> bool:
        changed = False
        if isinstance(target, dict) and isinstance(defaults, dict):
            for k, dv in defaults.items():
                if k not in target:
                    target[k] = self._copy_obj(dv)
                    changed = True
                else:
                    tv = target[k]
                    if isinstance(tv, dict) and isinstance(dv, dict):
                        if self._deep_merge_defaults(tv, dv):
                            changed = True
        return changed

    def _copy_obj(self, obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: self._copy_obj(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._copy_obj(v) for v in obj]
        return obj
