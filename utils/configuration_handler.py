from __future__ import annotations
from pathlib import Path
import sys
from typing import Any, Dict, Optional, Set
import tempfile
import shutil
import os
from loguru import logger

from utils.jsonc import JsoncParseError, jsonc
from utils.constants import Const

try:
    from jsonschema import (  # type: ignore
        validate as jsonschema_validate,
        ValidationError as JsonSchemaValidationError,
    )

    JSONSCHEMA_AVAILABLE = True
except Exception:
    JSONSCHEMA_AVAILABLE = False


class ConfigError(Exception):
    pass


class ConfigurationHandler:
    """
    Configuration handler with:
     - default config merge
     - supports `import` keys (global and inside nested dicts)
     - get_option / set_option using dot notation
     - tries to use jsonc.update (preserve comments), fallback to full atomic write
     - optional JSON Schema validation (if Const.DEFAULT_CONFIG_FILE_SCHEMA and jsonschema is installed)

    Strict behavior:
     - any JSON/JSONC parse error in user/default/imported/schema files -> pretty print error and exit immediately
    """

    def __init__(self, config_file: Optional[Path] = None):
        # Runtime config file (user file)
        self.config_file: Path = Path(config_file or Const.APP_CONFIG_FILE)
        self.config_file = self.config_file.expanduser().resolve()

        # Ensure parent exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        # Validate extension
        if self.config_file.suffix.lower() not in (".json", ".jsonc"):
            raise ConfigError("Config file must have .json or .jsonc extension")

        # Ensure default config exists somewhere: either Const.DEFAULT_CONFIG_FILE or Const.DEFAULT_CONFIG in memory
        self._default_file: Optional[Path] = getattr(Const, "DEFAULT_CONFIG_FILE", None)
        if self._default_file:
            self._default_file = Path(self._default_file).expanduser().resolve()

        # If user config not exists or empty -> create with defaults (prefer file if present)
        if not self.config_file.exists() or self.config_file.stat().st_size == 0:
            try:
                initial = {}
                if self._default_file and self._default_file.exists():
                    # strict load of default file (parse errors are fatal)
                    initial = self._load_jsonc_strict(self._default_file)
                else:
                    initial = getattr(Const, "DEFAULT_CONFIG", {}) or {}
                jsonc.write(self.config_file, initial)
                logger.info(
                    f"Created config file at {self.config_file} (wrote default config)."
                )
            except SystemExit:
                # _load_jsonc_strict already printed prettified error and exited.
                raise
            except Exception as e:
                logger.error(f"Failed to create default config file: {e}")
                # This is unexpected; treat as fatal for safety
                sys.exit(1)

        # If schema path provided, try to load
        self._schema_path: Optional[Path] = getattr(
            Const, "DEFAULT_CONFIG_FILE_SCHEMA", None
        )
        if self._schema_path:
            self._schema_path = Path(self._schema_path).expanduser().resolve()

    # -------------------------
    # Helpers: merge + imports + validation
    # -------------------------
    @staticmethod
    def _merge_dicts(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursive merge: override keys replace base; nested dicts are merged."""
        out = dict(base)  # shallow copy
        for k, v in override.items():
            if k in out and isinstance(out[k], dict) and isinstance(v, dict):
                out[k] = ConfigurationHandler._merge_dicts(out[k], v)
            else:
                out[k] = v
        return out

    def _resolve_imports_recursive(
        self,
        data: Any,
        visited: Optional[Set[Path]] = None,
        parent_base: Optional[Path] = None,
    ) -> Any:
        """
        Recursively traverse `data` and when encountering a dict with key "import",
        load and merge that file's data into the dict. `visited` prevents cycles.
        parent_base - file from which relative imports are resolved.

        NOTE: if an imported file has parse errors -> strict exit via _load_jsonc_strict
        """
        if visited is None:
            visited = set()

        if isinstance(data, dict):
            # If this dict has an import key, load file and merge
            if "import" in data:
                imp = data.pop("import")
                imp_path = Path(imp).expanduser()
                if not imp_path.is_absolute() and parent_base:
                    imp_path = (parent_base.parent / imp_path).resolve()
                else:
                    imp_path = imp_path.resolve()

                if imp_path in visited:
                    logger.warning(f"Skipping cyclic import {imp_path}")
                else:
                    visited.add(imp_path)
                    # strict load: will exit on parse errors
                    imported = self._load_jsonc_strict(imp_path)
                    imported = self._resolve_imports_recursive(
                        imported, visited, imp_path
                    )
                    # merge imported into current dict, keeping current keys as override
                    data = self._merge_dicts(imported, data)

            # Recursively resolve deeper
            for k, v in list(data.items()):
                data[k] = self._resolve_imports_recursive(v, visited, parent_base)
            return data

        if isinstance(data, list):
            return [
                self._resolve_imports_recursive(x, visited, parent_base) for x in data
            ]

        return data

    def _load_user_config(self) -> Dict[str, Any]:
        """Load raw user config, resolve imports (global and per-widget). Strict: parse errors -> exit."""
        # strict load of user config
        raw = self._load_jsonc_strict(self.config_file)

        resolved = self._resolve_imports_recursive(raw, set(), self.config_file)

        if not isinstance(resolved, dict):
            logger.critical("User config root must be a JSON object")
            sys.exit(1)

        return resolved

    def _load_default_config(self) -> Dict[str, Any]:
        """Load default config either from DEFAULT_CONFIG_FILE or in-memory Const.DEFAULT_CONFIG. Strict on parse errors."""
        if self._default_file and self._default_file.exists():
            # strict: parse errors in default config are fatal (developer error)
            default_raw = self._load_jsonc_strict(self._default_file)
            default = self._resolve_imports_recursive(
                default_raw, set(), self._default_file
            )
            if not isinstance(default, dict):
                logger.critical("Default config root must be a JSON object")
                sys.exit(1)
            return default
        return getattr(Const, "DEFAULT_CONFIG", {}) or {}

    def _validate_schema(self, data: Dict[str, Any]) -> None:
        """Optional JSON Schema validation if schema file present and jsonschema installed. Fail-fast on validation error."""
        if (
            not JSONSCHEMA_AVAILABLE
            or not self._schema_path
            or not self._schema_path.exists()
        ):
            return
        try:
            # strict load of schema file (parse errors -> exit)
            schema = self._load_jsonc_strict(self._schema_path)
            jsonschema_validate(instance=data, schema=schema)  # type: ignore
            return
        except JsonSchemaValidationError as e:  # type: ignore
            logger.critical(f"Configuration schema validation failed: {e.message}")
            sys.exit(1)
        except SystemExit:
            raise
        except Exception as e:
            logger.critical(f"Failed schema validation: {e}")
            sys.exit(1)

    def _load_merged(self) -> Dict[str, Any]:
        """Return merged config: DEFAULT_CONFIG <- user_config. Schema validation is strict."""
        default = self._load_default_config() or {}
        user = self._load_user_config() or {}
        merged = self._merge_dicts(default, user)
        # strict validation: will exit on failure
        self._validate_schema(merged)
        return merged

    # -------------------------
    # Public API
    # -------------------------
    def get_option(self, key: str, default: Any = None) -> Any:
        """Get option using dot notation from merged (default+user) config"""
        if not key:
            return default
        keys = key.split(".")
        data = self._load_merged()
        cur: Any = data
        for k in keys:
            if isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                return default
        return cur

    def set_option(self, key: str, value: Any) -> bool:
        """
        Set option using dot notation.
        Returns True if the on-disk user config file was changed.
        Tries jsonc.update first (preserve comments). Falls back to full atomic write.
        """
        if not key:
            return False

        # First: try in-place update via jsonc.update() (keeps comments)
        try:
            ok = jsonc.update(self.config_file, key, value)
            if ok:
                logger.info(f"Updated config (in-place): {key} = {value}")
                return True
        except Exception as e:
            logger.debug(f"jsonc.update failed or not applicable: {e}")

        # Fallback: modify user config dict and write atomically
        # Use strict loader to ensure we don't overwrite a syntactically invalid file
        user = self._load_user_config()
        d = user
        keys = key.split(".")
        for k in keys[:-1]:
            if k not in d or not isinstance(d[k], dict):
                d[k] = {}
            d = d[k]
        if d.get(keys[-1]) == value:
            logger.debug("No change in value; skip write.")
            return False
        d[keys[-1]] = value

        # atomic write: write to tmp file then move
        tmp_fd, tmp_path = tempfile.mkstemp(
            prefix=self.config_file.name, dir=str(self.config_file.parent)
        )
        os.close(tmp_fd)
        try:
            jsonc.write(Path(tmp_path), user)
            shutil.move(tmp_path, str(self.config_file))  # atomic replace on POSIX
            logger.info(f"Config written: {key} = {value}")
            return True
        except Exception as e:
            logger.error(f"Failed to write config file: {e}")
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
            return False

    def _load_jsonc_strict(self, path: Path) -> dict:
        """
        Strict loader: on any parse error produce pretty output and exit immediately,
        mirroring behavior from your utils/config_handler.py.
        """
        try:
            return jsonc.get_data(path)
        except JsoncParseError as e:
            # pretty error output with colors if available
            try:
                logger.opt(colors=True).error(e.pretty())
            except Exception:
                logger.critical("\n" + e.pretty())
            # Fail fast with explanatory message
            raise SystemExit(
                f"Configuration parsing failed for {path}. Fix the JSONC syntax and restart the app."
            )
        except Exception as e:
            logger.critical(f"Unexpected error while reading config {path}: {e}")
            raise SystemExit(1)
