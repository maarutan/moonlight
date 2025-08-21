from pathlib import Path
from typing import Optional, Dict
import imagehash
from PIL import Image

from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.image import Image as FImage
from fabric.hyprland.widgets import HyprlandWorkspaces
from fabric.utils import exec_shell_command_async

from config import TEMP_DIR, STATUS_BAR_LOCK_MODULES, APP_NAME, PLACEHOLDER_IMAGE
from utils import JsonManager

from gi.repository import GLib  # type: ignore


class WorkspacesPreview(Window):
    def __init__(self, max_visible_workspaces: int = 10) -> None:
        super().__init__(
            name="statusbar-workspaces-preview",
            layer="top",
            anchor="top left",
            exclusivity="normal",
            h_align="fill",
            h_expand=True,
        )
        self.preview_node = "workspaces.preview"
        self.HyprWorkS = HyprlandWorkspaces()
        self.current_active_workspace = str(self.HyprWorkS._active_workspace)
        self.json = JsonManager()
        self.max_visible_workspaces = max_visible_workspaces
        self.database: Dict[str, str] = {}

        self.tmp_preview_dir = Path(TEMP_DIR) / APP_NAME / "workspaces" / "preview"
        self.tmp_preview_dir.mkdir(parents=True, exist_ok=True)

        # заполняем плейсхолдерами
        for i in range(1, self.max_visible_workspaces + 1):
            self.database[str(i)] = PLACEHOLDER_IMAGE.as_posix()

        # создаём превью
        self.children = self._make_preview()

        # сразу запускаем обновление
        self._update_preview_async()

    def _make_preview(self) -> FImage:
        previews = self._list_previews()
        current_preview_path = previews.get(
            str(self.current_active_workspace),
            PLACEHOLDER_IMAGE.as_posix(),
        )
        candidate = Path(current_preview_path)
        if not self._is_valid_image(candidate):
            current_preview_path = PLACEHOLDER_IMAGE.as_posix()

        return FImage(
            name="statusbar-workspaces-preview-image",
            image_file=current_preview_path,
            size=128,
        )

    def _list_previews(self) -> Dict[str, str]:
        previews_dict = self.database.copy()
        for path in self.tmp_preview_dir.iterdir():
            if path.is_file():
                try:
                    ws_index = int(path.stem)
                    previews_dict[str(ws_index)] = path.as_posix()
                except ValueError:
                    continue
        try:
            self.json.update(STATUS_BAR_LOCK_MODULES, self.preview_node, previews_dict)
        except Exception:
            pass
        return previews_dict

    def _shot(self, save_to: str) -> bool:
        try:
            exec_shell_command_async(f"grim {save_to}")
            return True
        except Exception:
            return False

    def _screen_shot_handler_async(self, ws: str, cb) -> None:
        """Асинхронный снимок: сразу отдаём placeholder, потом догоняем готовым PNG."""
        target = self.tmp_preview_dir / f"{ws}.png"
        if not self._shot(target.as_posix()):
            cb(None)
            return

        def check_ready() -> bool:
            if self._is_valid_image(target):
                cb(target)
                return False  # снимаем idle callback
            return True  # проверим снова на следующем idle

        GLib.idle_add(check_ready)

    def __is_different(self, img1: str, img2: str, threshold: int = 5) -> bool:
        try:
            h1 = imagehash.average_hash(Image.open(img1))
            h2 = imagehash.average_hash(Image.open(img2))
            return (h1 - h2) > threshold
        except Exception:
            return True

    def _is_valid_image(self, path: Path) -> bool:
        try:
            if not path.exists() or path.stat().st_size == 0:
                return False
            with Image.open(path) as im:
                im.verify()
            return True
        except Exception:
            return False

    def _update_preview_async(self, workspace: Optional[str] = None) -> None:
        ws = workspace or self.current_active_workspace
        key = str(ws)
        prev_dict = self._list_previews()
        prev_path = prev_dict.get(key)

        def on_ready(saved: Optional[Path]):
            if not saved:
                return
            if prev_path and Path(prev_path).exists():
                if not self.__is_different(prev_path, saved.as_posix()):
                    return
            new_dict = prev_dict.copy()
            new_dict[key] = saved.as_posix()
            try:
                self.json.update(STATUS_BAR_LOCK_MODULES, self.preview_node, new_dict)
            except Exception:
                pass

        # запускаем асинхронный снимок
        self._screen_shot_handler_async(ws, on_ready)
