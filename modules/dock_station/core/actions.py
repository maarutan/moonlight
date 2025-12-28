import re
import shlex
import threading
import configparser
from pathlib import Path
from typing import TYPE_CHECKING

from fabric.utils import exec_shell_command, GLib
from loguru import logger

if TYPE_CHECKING:
    from ..dock import DockStation


class DockStationActions:
    def __init__(self, class_init: "DockStation"):
        self.conf = class_init
        self._cache: dict[str, str] = {}

    def _get_focused(self) -> str:
        return self.conf.hypr.data_activewindow().get("address")  # type: ignore

    def _normalize(self, name: str) -> str:
        return name.strip().lower().replace(" ", "").replace("-", "").replace("_", "")

    def _resolve_exec(self, app: str) -> str:
        norm_app = self._normalize(app)
        if norm_app in self._cache:
            return self._cache[norm_app]

        search_paths = [
            Path.home() / ".local/share/applications",
            Path("/usr/share/applications"),
        ]

        for sp in search_paths:
            if not sp.exists():
                continue
            for file in sp.glob("*.desktop"):
                try:
                    cp = configparser.ConfigParser(interpolation=None)
                    cp.read(file, encoding="utf-8")
                    if "Desktop Entry" not in cp:
                        continue
                    entry = cp["Desktop Entry"]

                    name = entry.get("Name", "")
                    wmclass = entry.get("StartupWMClass", "")
                    exec_cmd = entry.get("Exec", "")

                    if not exec_cmd:
                        continue

                    exec_cmd = re.sub(r"\s+%[fFuUdDnNickvm]", "", exec_cmd).strip()
                    cmd = shlex.split(exec_cmd)[0]

                    if wmclass and self._normalize(wmclass) == norm_app:
                        self._cache[norm_app] = cmd
                        return cmd

                    if name and norm_app in self._normalize(name):
                        self._cache[norm_app] = cmd
                        return cmd

                    if norm_app in self._normalize(file.stem):
                        self._cache[norm_app] = cmd
                        return cmd

                except Exception:
                    continue

        self._cache[norm_app] = app
        return app

    def handle_app(self, app: str, instances: list[dict]):
        if not instances:
            cmd = self._resolve_exec(app)
            threading.Thread(
                target=exec_shell_command, args=(f"nohup {cmd}",), daemon=True
            ).start()
        else:
            focused = self._get_focused()
            idx = next(
                (
                    i
                    for i, inst in enumerate(instances)
                    if inst.get("address") == focused
                ),
                -1,
            )
            next_inst = instances[(idx + 1) % len(instances)]
            exec_shell_command(
                f"hyprctl dispatch focuswindow address:{next_inst['address']}"
            )

    def move_to_workspace(self, app: str, ws: int):
        instances = self.conf.hypr.windows_for_app(app)
        self.handle_app(app, instances)
        exec_shell_command(f"hyprctl dispatch movetoworkspace {ws}")

    def fullscreen_app(self, app: str):
        instances = self.conf.hypr.windows_for_app(app)
        for inst in instances:
            exec_shell_command(f"hyprctl dispatch fullscreen address:{inst['address']}")

    def toggle_floating_app(self, app: str):
        instances = self.conf.hypr.windows_for_app(app)
        for inst in instances:
            exec_shell_command(
                f"hyprctl dispatch togglefloating address:{inst['address']}"
            )

    def fullscreen_window(self, window: dict):
        address = window.get("address")
        if address:
            exec_shell_command(f"hyprctl dispatch fullscreen address:{address}")

    def toggle_floating_window(self, window: dict):
        address = window.get("address")
        if address:
            exec_shell_command(f"hyprctl dispatch togglefloating address:{address}")

    def move_window_to_workspace(self, window: dict, ws: int):
        address = window.get("address")
        if address:
            exec_shell_command(
                f"hyprctl dispatch movetoworkspace address:{address} {ws}"
            )

    def close_window(self, window: dict):
        address = window.get("address")
        if address:
            exec_shell_command(f"hyprctl dispatch closewindow address:{address}")

    def close_app(self, ws: int, app: str):
        instances = self.conf.hypr.windows_for_app(app)
        for w in instances:
            ws_val = w.get("workspace")
            if isinstance(ws_val, dict):
                ws_val = ws_val.get("id", 1)
            if ws_val == ws:
                self.close_window(w)

    def pin_unpin(self, app: str) -> None:
        key = f"{self.conf.widget_name}.pinned"

        pinned = self.conf.items.pinned

        if app in pinned:
            pinned.remove(app)
        else:
            pinned.append(app)

        self.conf.confh.set_option(key, pinned)
        self.conf.config = self.conf.confh.get_option(self.conf.widget_name)
        GLib.idle_add(self.conf.items.build)

    def focus_window(self, window: dict):
        address = window.get("address")
        if address:
            exec_shell_command(f"hyprctl dispatch focuswindow address:{address}")
