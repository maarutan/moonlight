from pathlib import Path
from typing import Literal, Optional, Dict, Union
import uuid
from PIL import Image as PILImage

from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.hyprland.widgets import HyprlandWorkspaces
from fabric.utils import exec_shell_command_async

from utils.constants import Const
from fabric.widgets.image import Image as FabricImage

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
        if missing_behavior not in ("show", "hide"):
            raise ValueError("missing_behavior must be 'show' or 'hide'")

        self.missing_behavior = missing_behavior
        self.preview_node = "workspaces.preview"
        self.HyprWorkS = HyprlandWorkspaces()

        try:
            self.real_active_workspace = str(self.HyprWorkS._active_workspace)
        except Exception:
            self.real_active_workspace = "1"

        self.current_shown_workspace = self.real_active_workspace
        self.last_captured_active: Optional[str] = None
        self.max_visible_workspaces = max_visible_workspaces
        self.database: Dict[str, str] = {}
        self.img_size = image_size

        self.tmp_preview_dir = Const.TEMP_DIR / "workspaces" / "preview"
        self.tmp_preview_dir.mkdir(parents=True, exist_ok=True)

        for i in range(1, self.max_visible_workspaces + 1):
            self.database[str(i)] = ""

        initial_path = self._list_previews().get(self.current_shown_workspace, "")
        valid = self._is_valid_image(Path(initial_path)) if initial_path else False

        if not valid and self.missing_behavior == "hide":
            initial_path_to_use = None
        else:
            initial_path_to_use = (
                initial_path if valid else Const.PLACEHOLDER_IMAGE_GHOST.as_posix()
            )

        img_file_arg = (
            Const.PLACEHOLDER_IMAGE_GHOST.as_posix()
            if initial_path_to_use in (None, "", False)
            else initial_path_to_use
        )

        self.image_widget = FabricImage(
            name="statusbar-workspaces-preview-image",
            image_file=img_file_arg,
            h_expand=True,
            v_expand=True,
            h_align="center",
            v_align="center",
        )

        def build():
            return self.image_widget

        super().__init__(
            name="statusbar-workspaces-preview",
            layer="top",
            anchor=anchor_handler,
            exclusivity="none",
            margin=margin_handler,
            child=build(),
        )

        self._window_shown = False
        self._suspended = False

        if initial_path_to_use is None:
            self._suspended = True
            self._hide_image_widget()
            self._hide_window()
        else:
            self._show_image_widget()

    def _show_window(self, force: bool = False) -> None:
        if self._suspended and not force:
            return
        try:
            if self._window_shown:
                return
            if hasattr(self, "show_all"):
                self.show_all()
            elif hasattr(self, "show"):
                self.show()
            elif hasattr(self, "set_visible"):
                self.set_visible(True)
            self._window_shown = True
            self._suspended = False
        except Exception:
            logger.exception("show window failed")

    def _hide_window(self) -> None:
        try:
            if not self._window_shown:
                return
            if hasattr(self, "hide"):
                self.hide()
            elif hasattr(self, "set_visible"):
                self.set_visible(False)
            self._window_shown = False
        except Exception:
            logger.exception("hide window failed")

    def _show_image_widget(self) -> None:
        try:
            cur = getattr(self, "children", []) or []
            if self.image_widget not in cur:
                self.children = cur + [self.image_widget]
            self.image_widget.set_visible(True)
            self._suspended = False
            self._show_window(force=True)
        except Exception:
            logger.exception("show image widget failed")

    def _hide_image_widget(self) -> None:
        try:
            cur = getattr(self, "children", []) or []
            if self.image_widget in cur:
                self.children = [c for c in cur if c is not self.image_widget]
            self.image_widget.set_visible(False)
            if not self.children:
                self._hide_window()
        except Exception:
            logger.exception("hide image widget failed")

    def _list_previews(self) -> Dict[str, str]:
        previews = self.database.copy()
        try:
            for path in self.tmp_preview_dir.iterdir():
                if path.is_file():
                    try:
                        previews[str(int(path.stem))] = path.as_posix()
                    except ValueError:
                        pass
        except FileNotFoundError:
            pass
        return previews

    def _is_valid_image(self, path: Path) -> bool:
        try:
            if not path.exists() or path.stat().st_size == 0:
                return False
            with PILImage.open(path) as im:
                im.verify()
            return True
        except Exception:
            return False

    def _shot(self, save_to: str) -> bool:
        try:
            tmp = f"{save_to}.tmp-{uuid.uuid4().hex}"
            exec_shell_command_async(
                f'sh -c \'grim "{tmp}" && mv "{tmp}" "{save_to}"\''
            )
            return True
        except Exception:
            return False

    def _load_pixbuf_for_path(self, path: str) -> Optional[GdkPixbuf.Pixbuf]:
        try:
            return GdkPixbuf.Pixbuf.new_from_file_at_size(
                path, self.img_size, self.img_size
            )
        except Exception:
            try:
                return GdkPixbuf.Pixbuf.new_from_file(path)
            except Exception:
                return None

    def _wait_for_file_stable(self, path: Path, cb, max_checks=10, delay_ms=70):
        state = {"n": 0, "last": -1}

        def check():
            state["n"] += 1
            if not path.exists():
                return state["n"] < max_checks
            size = path.stat().st_size
            if size == state["last"] or state["n"] >= max_checks:
                cb(path)
                return False
            state["last"] = size
            return True

        GLib.timeout_add(delay_ms, check)

    def _screen_shot_handler_async(self, ws: str, cb) -> None:
        target = self.tmp_preview_dir / f"{ws}.png"
        if not self._shot(target.as_posix()):
            cb(None)
            return
        self._wait_for_file_stable(target, cb)

    def update_display_for_workspace(self, workspace: Union[str, int]) -> None:
        key = str(workspace)
        path = self._list_previews().get(key)
        if path:
            pixbuf = self._load_pixbuf_for_path(path)
            if pixbuf:
                self.image_widget.set_from_pixbuf(pixbuf)
                self._show_image_widget()
                self.current_shown_workspace = key
                return
        if self.missing_behavior == "show":
            self.image_widget.set_from_file(Const.PLACEHOLDER_IMAGE_GHOST.as_posix())
            self._show_image_widget()
        else:
            self._hide_image_widget()
            self._hide_window()
        self.current_shown_workspace = key

    def _update_preview_async(self, workspace: Union[str, int]) -> None:
        ws = str(workspace)

        def ready(path):
            if path:
                self.update_display_for_workspace(ws)

        self._screen_shot_handler_async(ws, ready)

    def set_update(self, workspace: Union[str, int]) -> None:
        key = str(workspace)
        try:
            self.real_active_workspace = str(self.HyprWorkS._active_workspace)
        except Exception:
            pass

        self.update_display_for_workspace(key)

        if self.last_captured_active != self.real_active_workspace:
            self.last_captured_active = self.real_active_workspace
            self._update_preview_async(self.real_active_workspace)

    def set_missing_behavior(self, behavior: Literal["show", "hide"]) -> None:
        self.missing_behavior = behavior
        self.update_display_for_workspace(self.current_shown_workspace)
