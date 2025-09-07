from pathlib import Path
from typing import Literal, Optional, Dict, Union
import uuid
from PIL import Image

from fabric.widgets.wayland import WaylandWindow as Window
from fabric.hyprland.widgets import HyprlandWorkspaces
from fabric.utils import exec_shell_command_async

from config import TEMP_DIR, STATUS_BAR_LOCK_MODULES, APP_NAME, PLACEHOLDER_IMAGE
from utils import JsonManager
from fabric.widgets.image import Image

from gi.repository import GLib, GdkPixbuf  # type: ignore
from loguru import logger


class WorkspacesPreview(Window):
    def __init__(
        self,
        max_visible_workspaces: int = 10,
        image_size: int = 300,
        anchor_handler: str = "top left",
        margin_handler: str = "0 30 0 30",
        missing_behavior: Literal["show", "hide"] = "hide",
    ) -> None:
        super().__init__(
            name="statusbar-workspaces-preview",
            layer="top",
            anchor=anchor_handler,
            exclusivity="none",
            margin=margin_handler,
        )
        if missing_behavior not in ("show", "hide"):
            raise ValueError("missing_behavior must be 'show' or 'hide'")
        self.missing_behavior = missing_behavior
        self.preview_node = "workspaces.preview"
        self.HyprWorkS = HyprlandWorkspaces()

        try:
            self.real_active_workspace = str(self.HyprWorkS._active_workspace)
        except Exception:
            self.real_active_workspace = "1"
        self.current_shown_workspace = str(self.real_active_workspace)
        self.last_captured_active: Optional[str] = None
        self.json = JsonManager()
        self.max_visible_workspaces = max_visible_workspaces
        self.database: Dict[str, str] = {}
        self.img_size = image_size
        self.tmp_preview_dir = Path(TEMP_DIR) / APP_NAME / "workspaces" / "preview"
        self.tmp_preview_dir.mkdir(parents=True, exist_ok=True)

        for i in range(1, self.max_visible_workspaces + 1):
            self.database[str(i)] = ""

        initial_path = self._list_previews().get(self.current_shown_workspace, "")
        valid = self._is_valid_image(Path(initial_path)) if initial_path else False

        if not valid and self.missing_behavior == "hide":
            initial_path_to_use = None
        else:
            initial_path_to_use = (
                initial_path if valid else PLACEHOLDER_IMAGE.as_posix()
            )
        if initial_path_to_use in [None, "", False]:
            img_file_arg = PLACEHOLDER_IMAGE.as_posix()
        else:
            img_file_arg = initial_path_to_use

        self.image_widget = Image(
            name="statusbar-workspaces-preview-image",
            image_file=img_file_arg,
            size=self.img_size,
            h_expand=True,
            v_expand=True,
            h_align="center",
            v_align="center",
        )
        self.children = []
        self._window_shown = False
        self._suspended = False
        if initial_path_to_use is None:
            self._suspended = True
            self._hide_image_widget()
            self._hide_window()
        else:
            self._suspended = False
            self._show_image_widget()

    def _show_window(self, force: bool = False) -> None:
        if self._suspended and not force:
            return
        try:
            if self._suspended and not force:
                return
            if getattr(self, "_window_shown", False):
                return
            if hasattr(self, "show_all"):
                try:
                    self.show_all()
                except Exception:
                    if hasattr(self, "show"):
                        self.show()
            elif hasattr(self, "show"):
                self.show()
            elif hasattr(self, "set_visible"):
                try:
                    self.set_visible(True)
                except Exception:
                    pass
            self._window_shown = True
            logger.debug("[WorkspacesPreview] window shown")
        except Exception:
            logger.exception("[WorkspacesPreview] failed to show window")

    def _hide_window(self) -> None:
        try:
            if not getattr(self, "_window_shown", False):
                return
            if hasattr(self, "hide"):
                try:
                    self.hide()
                except Exception:
                    if hasattr(self, "set_visible"):
                        try:
                            self.set_visible(False)
                        except Exception:
                            pass
            elif hasattr(self, "set_visible"):
                try:
                    self.set_visible(False)
                except Exception:
                    pass
            self._window_shown = False
            logger.debug("[WorkspacesPreview] window hidden")
        except Exception:
            logger.exception("[WorkspacesPreview] failed to hide window")

    def _show_image_widget(self) -> None:
        try:
            cur = getattr(self, "children", []) or []
            if self.image_widget not in cur:
                self.children = [c for c in cur if c is not self.image_widget] + [
                    self.image_widget
                ]
            if hasattr(self.image_widget, "set_visible"):
                try:
                    self.image_widget.set_visible(True)
                except Exception:
                    if hasattr(self.image_widget, "show"):
                        self.image_widget.show()
            elif hasattr(self.image_widget, "show"):
                self.image_widget.show()
            self._suspended = False
            self._show_window(force=True)
            logger.debug(
                "[WorkspacesPreview] image_widget shown; children=%s", self.children
            )
        except Exception:
            logger.exception("[WorkspacesPreview] failed to show image_widget")

    def _hide_image_widget(self) -> None:
        try:
            cur = getattr(self, "children", []) or []
            if self.image_widget in cur:
                self.children = [c for c in cur if c is not self.image_widget]
            if hasattr(self.image_widget, "set_visible"):
                try:
                    self.image_widget.set_visible(False)
                except Exception:
                    if hasattr(self.image_widget, "hide"):
                        self.image_widget.hide()
            elif hasattr(self.image_widget, "hide"):
                self.image_widget.hide()
            cur_after = getattr(self, "children", []) or []
            if len(cur_after) == 0:
                self._hide_window()
            logger.debug(
                "[WorkspacesPreview] image_widget hidden; children=%s", cur_after
            )
        except Exception:
            logger.exception("[WorkspacesPreview] failed to hide image_widget")

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
        try:
            tmp_name = f"{save_to}.tmp-{uuid.uuid4().hex}"
            cmd = f'sh -c \'grim "{tmp_name}" && mv "{tmp_name}" "{save_to}"\''
            exec_shell_command_async(cmd)
            return True
        except Exception:
            return False

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
        logger.debug(
            "[WorkspacesPreview] update_display_for_workspace called; missing_behavior=%s, window_shown=%s, children=%s",
            self.missing_behavior,
            getattr(self, "_window_shown", False),
            getattr(self, "children", []),
        )
        key = str(workspace)
        previews = self._list_previews()
        path = previews.get(key, "")
        p = Path(path) if path else None
        if p and p.exists() and p.stat().st_size > 0:
            pixbuf = self._load_pixbuf_for_path(path)
            if pixbuf is not None:
                try:
                    self.image_widget.set_from_pixbuf(pixbuf)
                    self._suspended = False
                    self._show_image_widget()
                    self.current_shown_workspace = key
                    return
                except Exception as e:
                    logger.warning(
                        f"[WorkspacesPreview] immediate set_from_pixbuf failed: {e}"
                    )
        if self.missing_behavior == "show":
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                    PLACEHOLDER_IMAGE.as_posix(), self.img_size, self.img_size
                )
                self.image_widget.set_from_pixbuf(pixbuf)
                self._suspended = False
                self._show_image_widget()
            except Exception:
                logger.debug(
                    "[WorkspacesPreview] failed to set placeholder", exc_info=True
                )
        else:
            self._suspended = True
            self._hide_image_widget()
            self._hide_window()
        self.current_shown_workspace = key
        logger.debug(f"[WorkspacesPreview] displayed placeholder/hid for ws {key}")

    def _update_preview_async(self, workspace: Union[str, int]) -> None:
        ws = str(workspace)
        prev_dict = self._list_previews()
        prev_path = prev_dict.get(ws)

        def on_ready(saved: Optional[Path]):
            if not saved:
                logger.debug(f"[WorkspacesPreview] shot failed/not stable for ws {ws}")
                return
            saved_path = saved.as_posix()
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

    def set_missing_behavior(self, behavior: Literal["show", "hide"]) -> None:
        if behavior not in ("show", "hide"):
            raise ValueError("behavior must be 'show' or 'hide'")
        self.missing_behavior = behavior
        cur_path = self._list_previews().get(self.current_shown_workspace, "")
        if cur_path and self._is_valid_image(Path(cur_path)):
            self._suspended = False
            self._show_image_widget()
        else:
            if self.missing_behavior == "show":
                try:
                    self._suspended = False
                    self.image_widget.set_from_file(PLACEHOLDER_IMAGE.as_posix())
                    self._show_image_widget()
                except Exception:
                    logger.debug(
                        "[WorkspacesPreview] failed to apply placeholder after behavior change",
                        exc_info=True,
                    )
            else:
                self._suspended = True
                self._hide_image_widget()
                self._hide_window()
