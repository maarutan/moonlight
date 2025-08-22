from pathlib import Path
from typing import Literal, Optional, Dict, Union
import uuid
import imagehash
from PIL import Image

from fabric.widgets.wayland import WaylandWindow as Window
from fabric.hyprland.widgets import HyprlandWorkspaces
from fabric.utils import exec_shell_command_async

from config import TEMP_DIR, STATUS_BAR_LOCK_MODULES, APP_NAME, PLACEHOLDER_IMAGE
from utils import JsonManager
from widgets import CustomImage

from gi.repository import GLib, GdkPixbuf  # type: ignore
from loguru import logger


class WorkspacesPreview(Window):
    def __init__(
        self,
        max_visible_workspaces: int = 10,
        image_size: int = 300,
        anchor_handler: str = "top left",
        margin_handler: str = "0 30 0 30",
    ) -> None:
        super().__init__(
            name="statusbar-workspaces-preview",
            layer="top",
            anchor=anchor_handler,
            exclusivity="none",
            margin=margin_handler,
        )

        self.preview_node = "workspaces.preview"
        self.HyprWorkS = HyprlandWorkspaces()
        self.real_active_workspace = str(self.HyprWorkS._active_workspace)
        self.current_shown_workspace = str(self.real_active_workspace)
        self.last_captured_active: Optional[str] = None

        self.json = JsonManager()
        self.max_visible_workspaces = max_visible_workspaces
        self.database: Dict[str, str] = {}
        self.img_size = int(image_size) or 128

        self.tmp_preview_dir = Path(TEMP_DIR) / APP_NAME / "workspaces" / "preview"
        self.tmp_preview_dir.mkdir(parents=True, exist_ok=True)

        for i in range(1, self.max_visible_workspaces + 1):
            self.database[str(i)] = PLACEHOLDER_IMAGE.as_posix()

        initial_path = self._list_previews().get(
            self.current_shown_workspace, PLACEHOLDER_IMAGE.as_posix()
        )
        if not self._is_valid_image(Path(initial_path)):
            initial_path = PLACEHOLDER_IMAGE.as_posix()

        self.image_widget = CustomImage(
            name="statusbar-workspaces-preview-image",
            image_file=initial_path,
            size=self.img_size,
            h_expand=True,
            v_expand=True,
            h_align="center",
            v_align="center",
        )
        self.children = [self.image_widget]

    def _list_previews(self) -> Dict[str, str]:
        previews_dict = self.database.copy()
        try:
            for path in self.tmp_preview_dir.iterdir():
                if path.is_file():
                    try:
                        ws_index = int(path.stem)
                        previews_dict[str(ws_index)] = path.as_posix()
                    except ValueError:
                        continue
        except FileNotFoundError:
            pass

        try:
            self.json.update(STATUS_BAR_LOCK_MODULES, self.preview_node, previews_dict)
        except Exception:
            pass

        return previews_dict

    def _is_valid_image(self, path: Path) -> bool:
        try:
            if not path.exists() or path.stat().st_size == 0:
                return False
            with Image.open(path) as im:
                im.verify()
            return True
        except Exception:
            return False

    def _shot(self, save_to: str) -> bool:
        """
        atomic: grim -> tmp -> mv
        """
        try:
            tmp_name = f"{save_to}.tmp-{uuid.uuid4().hex}"
            cmd = f'sh -c \'grim "{tmp_name}" && mv "{tmp_name}" "{save_to}"\''
            exec_shell_command_async(cmd)
            return True
        except Exception:
            return False

    def __is_different(self, img1: str, img2: str, threshold: int = 5) -> bool:
        try:
            h1 = imagehash.average_hash(Image.open(img1))
            h2 = imagehash.average_hash(Image.open(img2))
            return (h1 - h2) > threshold
        except Exception:
            return True

    def _load_pixbuf_for_path(self, path: str) -> Optional[GdkPixbuf.Pixbuf]:
        try:
            pb = GdkPixbuf.Pixbuf.new_from_file_at_size(
                path, self.img_size, self.img_size
            )
            return pb
        except Exception as e:
            logger.debug(
                f"[WorkspacesPreview] new_from_file_at_size failed for {path}: {e}"
            )
            try:
                pb = GdkPixbuf.Pixbuf.new_from_file(path)
                return pb
            except Exception as e2:
                logger.debug(
                    f"[WorkspacesPreview] new_from_file failed for {path}: {e2}"
                )
                return None

    def _wait_for_file_stable(
        self, path: Path, cb, max_checks: int = 10, delay_ms: int = 70
    ):
        checks = {"n": 0, "last_size": -1}

        def _checker() -> bool:
            checks["n"] += 1
            try:
                if not path.exists():
                    if checks["n"] >= max_checks:
                        cb(None)
                        return False
                    return True
                size = path.stat().st_size
            except Exception:
                size = 0

            if size == 0:
                if checks["n"] >= max_checks:
                    cb(None)
                    return False
                return True

            if size == checks["last_size"]:
                cb(path)
                return False

            checks["last_size"] = size
            if checks["n"] >= max_checks:
                cb(path)
                return False

            return True

        GLib.timeout_add(delay_ms, _checker)

    def _screen_shot_handler_async(self, ws: str, cb) -> None:
        target = self.tmp_preview_dir / f"{ws}.png"
        if not self._shot(target.as_posix()):
            cb(None)
            return
        self._wait_for_file_stable(target, cb, max_checks=12, delay_ms=70)

    def update_display_for_workspace(self, workspace: Union[str, int]) -> None:
        key = str(workspace)
        previews = self._list_previews()
        path = previews.get(key, PLACEHOLDER_IMAGE.as_posix())

        p = Path(path)
        if p.exists() and p.stat().st_size > 0:
            pixbuf = self._load_pixbuf_for_path(path)
            if pixbuf is not None:
                try:
                    self.image_widget.set_from_pixbuf(pixbuf)
                    logger.info(
                        f"[WorkspacesPreview] displayed preview for ws {key}: {path}"
                    )
                    self.current_shown_workspace = key
                    return
                except Exception as e:
                    logger.warning(
                        f"[WorkspacesPreview] immediate set_from_pixbuf failed: {e}"
                    )

        # fallback -> placeholder
        try:
            self.image_widget.set_from_file(PLACEHOLDER_IMAGE.as_posix())
        except Exception:
            pass
        self.current_shown_workspace = key
        logger.debug(f"[WorkspacesPreview] displayed placeholder for ws {key}")

    def _update_preview_async(self, workspace: Union[str, int]) -> None:
        ws = str(workspace)
        prev_dict = self._list_previews()
        prev_path = prev_dict.get(ws)

        def on_ready(saved: Optional[Path]):
            if not saved:
                logger.debug(f"[WorkspacesPreview] shot failed/not stable for ws {ws}")
                return
            saved_path = saved.as_posix()

            if prev_path and Path(prev_path).exists():
                try:
                    if not self.__is_different(prev_path, saved_path):
                        logger.debug(
                            f"[WorkspacesPreview] image for ws {ws} didn't change"
                        )
                        return
                except Exception:
                    pass

            new_dict = prev_dict.copy()
            new_dict[ws] = saved_path
            try:
                self.json.update(STATUS_BAR_LOCK_MODULES, self.preview_node, new_dict)
            except Exception:
                pass

            logger.info(
                f"[WorkspacesPreview] new preview ready for ws {ws}: {saved_path}"
            )
            self.update_display_for_workspace(ws)

        self._screen_shot_handler_async(ws, on_ready)

    def set_update(self, workspace: Union[str, int]) -> None:
        key = str(workspace)

        old_real = self.real_active_workspace
        try:
            self.real_active_workspace = str(self.HyprWorkS._active_workspace)
        except Exception:
            logger.debug("[WorkspacesPreview] failed to refresh real_active_workspace")

        if old_real != self.real_active_workspace:
            logger.info(
                f"[WorkspacesPreview] real active changed {old_real} -> {self.real_active_workspace}; reset last_captured"
            )
            self.last_captured_active = None
            if self.last_captured_active != self.real_active_workspace:
                self.last_captured_active = self.real_active_workspace
                try:
                    self._update_preview_async(self.real_active_workspace)
                except Exception:
                    logger.warning(
                        f"[WorkspacesPreview] failed to start initial capture for new active {self.real_active_workspace}"
                    )

        logger.debug(
            f"[WorkspacesPreview] set_update called for ws {key}; real_active={self.real_active_workspace}; shown={self.current_shown_workspace}; last_captured={self.last_captured_active}"
        )

        if self.real_active_workspace == key:
            logger.info(
                f"[WorkspacesPreview] SKIP capture for ws {key} (it's real active). Just show."
            )
            try:
                self.update_display_for_workspace(key)
            except Exception:
                logger.debug(f"[WorkspacesPreview] failed to display for {key}")
            return

        logger.info(f"[WorkspacesPreview] SHOW ONLY for ws {key} (no background shot)")
        try:
            self.update_display_for_workspace(key)
        except Exception:
            logger.debug(f"[WorkspacesPreview] immediate display failed for ws {key}")

        if self.last_captured_active != self.real_active_workspace:
            logger.info(
                f"[WorkspacesPreview] scheduling one-time capture for real active ws {self.real_active_workspace}"
            )
            self.last_captured_active = self.real_active_workspace
            try:
                self._update_preview_async(self.real_active_workspace)
            except Exception:
                logger.warning(
                    f"[WorkspacesPreview] failed to start one-time capture for active {self.real_active_workspace}"
                )

        return
