import re
import shlex
import threading
import configparser
from pathlib import Path
from typing import TYPE_CHECKING

from fabric.utils import exec_shell_command

if TYPE_CHECKING:
    from ..dock import Dock

from gi.repository import Gdk  # type: ignore
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.box import Box
from fabric.widgets.button import Button
from fabric.widgets.label import Label


class DockAction:
    def __init__(self, cfg: "Dock"):
        self._cfg = cfg
        self._cache: dict[str, str] = {}

    def _get_focused(self) -> str:
        try:
            return (
                self._cfg.json.loads(
                    self._cfg.conn.send_command("j/activewindow").reply.decode()
                ).get("address", "")
                or ""
            )
        except Exception:
            return ""

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

    def menu(self, app, instances): ...
