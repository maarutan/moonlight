from fabric.widgets.wayland import WaylandWindow as Window
from typing import TYPE_CHECKING, Literal, Optional, Dict, Any
from utils.constants import Const
from fabric.utils import GdkPixbuf, exec_shell_command_async, GLib
from fabric.widgets.image import Image

if TYPE_CHECKING:
    from .dock import DockStation

import os
import time
import shlex
import subprocess
from pathlib import Path


class WindowPreviewPopup(Window):
    def __init__(self, class_init: "DockStation"):
        self.conf = class_init
        self.is_hidden = True
        super().__init__(
            name=self.conf.widget_name + "-preview",
            anchor="bottom center",
            h_align="center",
            v_align="center",
            h_expand=True,
            v_expand=True,
            all_visible=True,
            margin="0px 0px 150px 0px",
        )
        self.DIR_PATHS: Path = (
            Const.TEMP_DIRECTORY / Const.APPLICATION_NAME / "dock_preview"
        )
        self.DIR_PATHS.mkdir(parents=True, exist_ok=True)
        self._screenshots_by_app: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self._watchers: Dict[str, int] = {}
        self._last_capture: Dict[str, float] = {}
        self.image_widget = Image(
            size=(300, 200),
        )
        self.add(self.image_widget)
        self._set_image_file(None)

    def toggle(self, action: Literal["show", "hide", "auto"] = "auto"):
        if action == "auto":
            action = "show" if self.is_hidden else "hide"
        if action == "show":
            self.is_hidden = False
            self.show()
        elif action == "hide":
            self.is_hidden = True
            self.hide()

    def _next_free_index(self, app_shots: Dict[str, Dict[str, Any]]) -> int:
        used = {info["index"] for info in app_shots.values()}
        i = 1
        while i in used:
            i += 1
        return i

    def _path_for_index(self, app_name: str, index: int) -> str:
        filename = f"{app_name}_{index}.png"
        return str(self.DIR_PATHS / filename)

    def _run_grim(self, geometry: str, outpath: str) -> None:
        os.makedirs(os.path.dirname(outpath), exist_ok=True)
        cmd = f"grim -g '{geometry}' {shlex.quote(outpath)}"
        try:
            exec_shell_command_async(cmd)
        except Exception:
            try:
                subprocess.Popen(
                    ["grim", "-g", geometry, outpath],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception:
                pass

    def sync_with_clients(self) -> None:
        clients = self.conf.hypr.data_clients()
        current_by_app: Dict[str, set] = {}
        for c in clients:
            name = (c.get("initialClass") or c.get("class") or "").strip()
            if not name:
                continue
            addr = c.get("address")
            if not addr:
                continue
            current_by_app.setdefault(name, set()).add(addr)
        for app, stored in list(self._screenshots_by_app.items()):
            current_addrs = current_by_app.get(app, set())
            to_delete = [addr for addr in stored.keys() if addr not in current_addrs]
            for addr in to_delete:
                info = stored.pop(addr, None)
                if info:
                    path = info.get("path")
                    if path and os.path.exists(path):
                        try:
                            os.remove(path)
                        except Exception:
                            pass
            if not stored:
                self._screenshots_by_app.pop(app, None)

    def _get_current_workspace_id(self) -> Optional[int]:
        monitors = self.conf.hypr.data_monitors() or {}
        for m in monitors.values():
            raw = m.get("raw") or {}
            if raw.get("focused"):
                aw = raw.get("activeWorkspace") or {}
                wid = aw.get("id")
                if wid is not None:
                    return int(wid)
        aw = self.conf.hypr.data_activewindow() or {}
        ws = (aw.get("workspace") or {}) or {}
        wid = ws.get("id")
        if wid is not None:
            return int(wid)
        clients = self.conf.hypr.data_clients()
        focused = next((c for c in clients if c.get("focus")), None)
        if focused:
            wid = (focused.get("workspace") or {}).get("id")
            if wid is not None:
                return int(wid)
        return None

    def _set_image_file(self, path: Optional[str]) -> None:
        target = (
            path
            if path and os.path.exists(path)
            else Const.PLACEHOLDER_IMAGE_GHOST.as_posix()
        )
        alloc = self.image_widget.get_size_request()
        width, height = (
            alloc.width if alloc.width > 0 else 300,
            alloc.height if alloc.height > 0 else 200,
        )
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(target, width, height, True)
        self.image_widget.set_from_pixbuf(pixbuf)
        self.image_widget.queue_draw()

    def _watch_file(self, path: str, timeout_ms: int = 3000, interval_ms: int = 100):
        if not path or path in self._watchers:
            return
        attempts = int(timeout_ms / interval_ms)
        state = {"left": attempts, "last_size": -1, "stable_count": 0}

        def tick():
            if not os.path.exists(path):
                state["left"] -= 1
                return state["left"] > 0

            size = os.path.getsize(path)
            if size == 0:
                state["left"] -= 1
                return state["left"] > 0

            if size == state["last_size"]:
                state["stable_count"] += 1
            else:
                state["stable_count"] = 0
            state["last_size"] = size

            if state["stable_count"] >= 2:  # два интервала подряд размер не менялся
                try:
                    self._set_image_file(path)
                except Exception:
                    self._set_image_file(None)
                sid = self._watchers.pop(path, None)
                if sid:
                    GLib.source_remove(sid)
                return False

            state["left"] -= 1
            if state["left"] <= 0:
                self._set_image_file(None)
                sid = self._watchers.pop(path, None)
                if sid:
                    GLib.source_remove(sid)
                return False
            return True

        source_id = GLib.timeout_add(interval_ms, tick)
        self._watchers[path] = source_id

    def screenshot(self, name: str) -> Optional[Dict[int, str]]:
        self.sync_with_clients()
        clients = self.conf.hypr.data_clients()
        wc = self.conf.hypr.windows_and_counts()
        count = wc.get(name, 0)
        if count == 0:
            if name in self._screenshots_by_app:
                for info in self._screenshots_by_app.pop(name, {}).values():
                    p = info.get("path")
                    if p and os.path.exists(p):
                        try:
                            os.remove(p)
                        except Exception:
                            pass
            self._set_image_file(None)
            return None
        active_ws = self._get_current_workspace_id()
        matches = [
            c
            for c in clients
            if (c.get("initialClass") or c.get("class") or "").lower() == name.lower()
            and c.get("mapped", False)
        ]
        matches_in_ws = (
            [c for c in matches if (c.get("workspace") or {}).get("id") == active_ws]
            if active_ws is not None
            else matches
        )
        app_shots = self._screenshots_by_app.setdefault(name, {})
        if not matches_in_ws:
            if app_shots:
                outmap = {info["index"]: info["path"] for info in app_shots.values()}
                preferred = outmap.get(min(outmap.keys())) if outmap else None
                if preferred and os.path.exists(preferred):
                    self._set_image_file(preferred)
                else:
                    self._set_image_file(None)
                return outmap
            else:
                self._set_image_file(None)
                return None
        now = time.time()
        last = self._last_capture.get(name, 0)
        if now - last < 0.35:
            pass
        self._last_capture[name] = now
        if len(matches_in_ws) == 1:
            client = matches_in_ws[0]
            addr = client.get("address") or str(client.get("pid", time.time()))
            if addr not in app_shots:
                desired_index = 1
                used = {info["index"] for info in app_shots.values()}
                if desired_index in used:
                    desired_index = self._next_free_index(app_shots)
                app_shots[addr] = {
                    "index": desired_index,
                    "path": self._path_for_index(name, desired_index),
                }
            idx = app_shots[addr]["index"]
            outpath = self._path_for_index(name, idx)
            x, y = client["at"]
            w, h = client["size"]
            geometry = f"{x},{y} {w}x{h}"
            self._run_grim(geometry, outpath)
            app_shots[addr]["path"] = outpath
            self._watch_file(outpath)
            return {info["index"]: info["path"] for info in app_shots.values()}
        for client in matches_in_ws:
            addr = client.get("address") or str(client.get("pid", time.time()))
            if addr not in app_shots:
                idx = self._next_free_index(app_shots)
                app_shots[addr] = {
                    "index": idx,
                    "path": self._path_for_index(name, idx),
                }
                x, y = client["at"]
                w, h = client["size"]
                geometry = f"{x},{y} {w}x{h}"
                outpath = self._path_for_index(name, idx)
                self._run_grim(geometry, outpath)
                app_shots[addr]["path"] = outpath
                self._watch_file(outpath)
        focused_client = next(
            (c for c in matches_in_ws if c.get("focus")), matches_in_ws[0]
        )
        faddr = focused_client.get("address") or str(
            focused_client.get("pid", time.time())
        )
        if faddr in app_shots:
            idx = app_shots[faddr]["index"]
            outpath = self._path_for_index(name, idx)
            x, y = focused_client["at"]
            w, h = focused_client["size"]
            geometry = f"{x},{y} {w}x{h}"
            self._run_grim(geometry, outpath)
            app_shots[faddr]["path"] = outpath
            self._watch_file(outpath)
        return {info["index"]: info["path"] for info in app_shots.values()}

    def get_screenshots_for(self, name: str) -> Dict[int, str]:
        app_shots = self._screenshots_by_app.get(name, {})
        return {info["index"]: info["path"] for info in app_shots.values()}

    def remove_all_for_app(self, name: str) -> None:
        app_shots = self._screenshots_by_app.pop(name, {})
        for info in app_shots.values():
            p = info.get("path")
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass
