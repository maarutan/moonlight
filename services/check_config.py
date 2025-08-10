import hashlib
import shutil
from pathlib import Path
from typing import List

from gi.repository import GObject, GLib  # type: ignore
from fabric.core.service import Service
from utils import JsonManager
from config import STATUS_BAR_CONFIG, APP_NAME


class CheckConfig(Service):
    __gsignals__ = {"config-changed": (GObject.SignalFlags.RUN_FIRST, None, ())}

    def __init__(self, config_lists: List[str] = None):
        super().__init__()
        self.json = JsonManager()
        self.config_lists = config_lists or [STATUS_BAR_CONFIG]

        self.local_share_path = Path.home() / ".local" / "share" / APP_NAME
        self.local_share_path.mkdir(parents=True, exist_ok=True)

        for cfg in self.config_lists:
            src = Path(cfg)
            dst = self.local_share_path / src.name
            if not dst.exists():
                shutil.copy2(src, dst)

        GLib.timeout_add_seconds(2, self._check_files)

    def _file_hash(self, path: Path) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()

    def _check_files(self) -> bool:
        changed = False

        for src_path_str in self.config_lists:
            src_path = Path(src_path_str)
            local_path = self.local_share_path / src_path.name

            if not local_path.exists():
                shutil.copy2(src_path, local_path)
                continue

            src_hash = self._file_hash(src_path)
            local_hash = self._file_hash(local_path)

            if src_hash != local_hash:
                print(f"[INFO] Config changed detected: {src_path}")
                shutil.copy2(src_path, local_path)
                changed = True

        if changed:
            self.emit("config-changed")

        return True
