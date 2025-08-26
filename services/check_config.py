import hashlib
import shutil
from pathlib import Path
from typing import Dict, List

from gi.repository import GObject, GLib  # type: ignore
from fabric.core.service import Service
from utils import JsonManager
from config import STATUS_BAR_CONFIG, APP_NAME, STYLES_DIR


class CheckConfig(Service):
    __gsignals__ = {"config-changed": (GObject.SignalFlags.RUN_FIRST, None, ())}

    def __init__(self, config_lists: List[str] = None):  # type: ignore
        super().__init__()
        self.json = JsonManager()
        self.config_lists = config_lists or [STATUS_BAR_CONFIG, STYLES_DIR]

        self.local_share_path = Path.home() / ".local" / "share" / APP_NAME
        self.local_share_path.mkdir(parents=True, exist_ok=True)

        # initial copy (file or directory)
        for cfg in self.config_lists:
            src = Path(cfg)
            if not src.exists():
                print(f"[WARN] Source not found: {src}")
                continue
            dst = self.local_share_path / src.name
            try:
                if src.is_dir():
                    if dst.exists():
                        # keep existing (we will check later)
                        continue
                    shutil.copytree(src, dst)
                else:
                    if not dst.exists():
                        shutil.copy2(src, dst)
            except Exception as e:
                print(f"[ERROR] initial copy failed for {src}: {e}")

        # start periodic checker
        GLib.timeout_add_seconds(2, self._check_files)

    def _file_hash(self, path: Path) -> str:
        """Return sha256 hex digest for a file. If path not file -> empty string."""
        if not path.is_file():
            return ""
        h = hashlib.sha256()
        try:
            with path.open("rb") as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    h.update(chunk)
        except Exception as e:
            print(f"[ERROR] hashing {path}: {e}")
            return ""
        return h.hexdigest()

    def _build_file_map(self, root: Path) -> Dict[str, str]:
        """
        Walk directory and return map: relative_path (posix) -> sha256.
        Only regular files are included. If root doesn't exist -> empty dict.
        """
        result: Dict[str, str] = {}
        if not root.exists():
            return result
        for p in root.rglob("*"):
            if p.is_file():
                try:
                    rel = p.relative_to(root).as_posix()
                except Exception:
                    # fallback to name if relative path fails
                    rel = p.name
                result[rel] = self._file_hash(p)
        return result

    def _replace_local(self, src: Path, dst: Path) -> None:
        """
        Replace dst with copy of src. Works for files and directories.
        """
        try:
            if dst.exists():
                if dst.is_dir():
                    shutil.rmtree(dst)
                else:
                    dst.unlink()
            if src.is_dir():
                shutil.copytree(src, dst)
            else:
                # ensure parent exists
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
        except Exception as e:
            print(f"[ERROR] replacing {dst} from {src}: {e}")

    def _check_files(self) -> bool:
        """
        Returns True to keep the GLib timeout running.
        Emits 'config-changed' if any monitored file/dir changed.
        """
        changed = False

        for src_path_str in self.config_lists:
            src_path = Path(src_path_str)
            local_path = self.local_share_path / src_path.name

            # If source vanished, skip (or optionally remove local copy).
            if not src_path.exists():
                # Option: remove local copy if source was removed. For now warn and continue.
                print(f"[WARN] Source disappeared: {src_path}")
                continue

            # If local copy missing -> create it and mark changed
            if not local_path.exists():
                print(f"[INFO] Local copy missing, creating: {local_path}")
                self._replace_local(src_path, local_path)
                changed = True
                continue

            # File handling
            if src_path.is_file():
                src_hash = self._file_hash(src_path)
                local_hash = self._file_hash(local_path)
                if src_hash != local_hash:
                    print(f"[INFO] File changed: {src_path}")
                    self._replace_local(src_path, local_path)
                    changed = True

            # Directory handling
            elif src_path.is_dir():
                src_map = self._build_file_map(src_path)
                local_map = self._build_file_map(local_path)

                # Quick checks: different sets of keys (added/removed/renamed files)
                if set(src_map.keys()) != set(local_map.keys()):
                    print(f"[INFO] Directory content changed (names): {src_path}")
                    self._replace_local(src_path, local_path)
                    changed = True
                    continue

                # Same file names, check hashes
                for rel, shash in src_map.items():
                    lhash = local_map.get(rel, "")
                    if shash != lhash:
                        print(f"[INFO] File changed inside directory: {src_path}/{rel}")
                        self._replace_local(src_path, local_path)
                        changed = True
                        break

            else:
                print(f"[WARN] Unsupported path type (not file/dir): {src_path}")

        if changed:
            try:
                self.emit("config-changed")
            except Exception as e:
                print(f"[ERROR] emitting signal: {e}")

        return True
