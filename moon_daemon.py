#!/usr/bin/env python3
import os
import sys
import time
import signal
from pathlib import Path
from typing import Dict, Tuple, Iterable
import shutil

from config import (
    PID_FILE,
    LOCAL_DIR,
    APP_NAME,
    CAVA_APP_DIR,
    CONFIG_FILE,
    DOCK_STATION_CONFIG,
    STATUS_BAR_DIR,
    APP_ASSETS,
)

StatT = Tuple[int, int]  # (mtime_ns, size)


class Daemon:
    def __init__(self, watch_dirs: list[str | Path] | None = None, interval: int = 2):
        self.interval = interval
        defaults = (
            [
                STATUS_BAR_DIR,
                DOCK_STATION_CONFIG,
                CAVA_APP_DIR,
                APP_ASSETS,
                CONFIG_FILE,
            ]
            if watch_dirs is None
            else watch_dirs
        )

        self.watch_roots: list[Path] = self._normalize_paths(defaults)

        self.local_dir = Path(LOCAL_DIR / APP_NAME).expanduser().resolve()
        self.pid_file = Path(PID_FILE).expanduser().resolve()
        self.last_snapshot: Dict[Tuple[Path, object], StatT] = {}

    # ---------- utils ----------
    @staticmethod
    def _normalize_paths(paths: Iterable[str | Path]) -> list[Path]:
        out: list[Path] = []
        for p in paths:
            pp = Path(p).expanduser()
            try:
                pp = pp.resolve(strict=False)
            except Exception:
                # На всякий случай оставим как есть, но это редкость
                pass
            out.append(pp)
        return out

    @staticmethod
    def _file_stat(p: Path) -> StatT:
        st = p.stat()
        return (
            int(getattr(st, "st_mtime_ns", int(st.st_mtime * 1e9))),
            int(st.st_size),
        )

    # ---------- snapshot & diff ----------
    def _take_snapshot(self) -> Dict[Tuple[Path, object], StatT]:
        """
        Ключ:
          - для директорий: (root_dir, rel_path: Path)
          - для одиночных файлов: (root_parent, file_name: str)
        Значение: (mtime_ns, size)
        """
        snapshot: Dict[Tuple[Path, object], StatT] = {}
        for root in self.watch_roots:
            if not root.exists():
                print(f"[WARN] Путь не существует и будет пропущен: {root}")
                continue

            if root.is_file():
                try:
                    key = (root.parent, root.name)  # rel часть = str
                    snapshot[key] = self._file_stat(root)
                except Exception as e:
                    print(f"[WARN] Не удалось прочитать {root}: {e}")
                continue

            # Директория
            try:
                for file in root.rglob("*"):
                    if file.is_file():
                        try:
                            key = (root, file.relative_to(root))  # rel = Path
                            snapshot[key] = self._file_stat(file)
                        except Exception as e:
                            print(f"[WARN] Не удалось прочитать {file}: {e}")
            except Exception as e:
                print(f"[WARN] Ошибка обхода {root}: {e}")
        return snapshot

    @staticmethod
    def _diff(
        old: Dict[Tuple[Path, object], StatT], new: Dict[Tuple[Path, object], StatT]
    ):
        old_keys = set(old.keys())
        new_keys = set(new.keys())
        added = new_keys - old_keys
        deleted = old_keys - new_keys
        common = old_keys & new_keys
        changed = {k for k in common if old[k] != new[k]}
        return added, changed, deleted

    # ---------- syncing ----------
    def _target_path(self, root: Path, rel) -> Path:
        """
        Для одиночного файла rel = str (имя файла) → кладём в LOCAL_DIR/rel
        Для директории rel = Path → кладём в LOCAL_DIR/root.name/rel
        """
        if isinstance(rel, str):
            return self.local_dir / rel
        return self.local_dir / root.name / rel

    def _sync_added_or_changed(
        self,
        snapshot: Dict[Tuple[Path, object], StatT],
        keys: Iterable[Tuple[Path, object]],
    ):
        for root, rel in keys:
            src = (root / rel) if not isinstance(rel, str) else (root / rel)
            try:
                data = src.read_bytes()
            except Exception as e:
                print(f"[WARN] Не удалось прочитать при синхронизации {src}: {e}")
                continue
            dst = self._target_path(root, rel)
            dst.parent.mkdir(parents=True, exist_ok=True)
            try:
                with open(dst, "wb") as f:
                    f.write(data)
            except Exception as e:
                print(f"[WARN] Не удалось записать {dst}: {e}")

    def _remove_deleted(self, keys: Iterable[Tuple[Path, object]]):
        for root, rel in keys:
            dst = self._target_path(root, rel)
            if dst.exists():
                try:
                    dst.unlink()
                    # аккуратно чистим пустые директории вверх до LOCAL_DIR
                    parent = dst.parent
                    while parent != self.local_dir and parent.exists():
                        try:
                            parent.rmdir()
                        except OSError:
                            break
                        parent = parent.parent
                except Exception as e:
                    print(f"[WARN] Не удалось удалить {dst}: {e}")

    # ---------- pid & signal ----------
    def _get_pid(self) -> int | None:
        if not self.pid_file.exists():
            return None
        try:
            return int(self.pid_file.read_text().strip())
        except Exception:
            return None

    def _send_reload_signal(self):
        pid = self._get_pid()
        if pid is None:
            print(f"[ERROR] Не найден PID файл {self.pid_file}")
            return
        try:
            os.kill(pid, signal.SIGHUP)
            print(f"[INFO] Послан SIGHUP → {APP_NAME} (PID={pid})")
        except ProcessLookupError:
            print(f"[WARN] Процесс PID={pid} не найден")
        except Exception as e:
            print(f"[ERROR] {e}")

    def _clear_local_dir(self):
        """Полностью очищает каталог приложения внутри LOCAL_DIR."""
        if self.local_dir.exists():
            print(f"[WARN] Очищаем LOCAL_DIR: {self.local_dir}")
            for item in self.local_dir.iterdir():
                try:
                    if item.is_file() or item.is_symlink():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                except Exception as e:
                    print(f"[WARN] Не удалось удалить {item}: {e}")
        else:
            self.local_dir.mkdir(parents=True, exist_ok=True)

    # ---------- main loop ----------
    def run(self):
        print(f"[INFO] {APP_NAME} Daemon запущен. Следим за:")
        for d in self.watch_roots:
            exists = "OK" if d.exists() else "MISSING"
            print(f"   - {d} [{exists}]")
        print(f"[INFO] Синхронизация → {self.local_dir}")

        while True:
            snapshot = self._take_snapshot()
            added, changed, deleted = self._diff(self.last_snapshot, snapshot)

            if added or changed or deleted:
                # Проверка: если только изменения (~), но хеши совпадают → сброс
                noisy = []
                for k in changed:
                    root, rel = k
                    src = (root / rel) if not isinstance(rel, str) else (root / rel)
                    try:
                        old_data = (root / rel).read_bytes()
                        new_data = (root / rel).read_bytes()
                        if old_data == new_data:
                            noisy.append(k)
                    except Exception:
                        pass

                if noisy and not added and not deleted:
                    # Бесконечные «~» без реальных изменений
                    self._clear_local_dir()
                    self._sync_added_or_changed(snapshot, snapshot.keys())
                    print(
                        "[INFO] Обнаружен шум изменений → LOCAL_DIR очищен и пересобран"
                    )
                else:
                    print(
                        f"[INFO] Δ изменения: +{len(added)}, ~{len(changed)}, -{len(deleted)}"
                    )
                    self._sync_added_or_changed(snapshot, added | changed)
                    self._remove_deleted(deleted)

                self._send_reload_signal()
                self.last_snapshot = snapshot

            time.sleep(self.interval)


def main():
    # ВАЖНО: разворачивай '~' и указывай реальные пути
    watch = [
        STATUS_BAR_DIR,
        DOCK_STATION_CONFIG,
        CAVA_APP_DIR,
        APP_ASSETS,
        CONFIG_FILE,
    ]
    d = Daemon(watch_dirs=watch, interval=2)
    d.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("⛔ Остановлено вручную")
        sys.exit(0)
