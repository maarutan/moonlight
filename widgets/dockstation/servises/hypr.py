from fabric.hyprland import Hyprland
from typing import TYPE_CHECKING, Dict, Any
import json

if TYPE_CHECKING:
    from ..dock import DockStation


class Hypr:
    def __init__(self, dockstation: "DockStation"):
        self.dockstation = dockstation
        self.hyprctl = Hyprland()

    def _send_json(self, cmd: str) -> dict | None:
        reply = Hyprland.send_command(cmd)
        if not reply.reply:
            return None
        return json.loads(reply.reply.decode())

    def windows_for_app(self, app_name: str) -> list[dict]:
        instances: list[dict] = []
        for client in self.data_clients() or []:
            name = client.get("initialClass") or client.get("class") or ""
            if name.lower() == app_name.lower():
                instances.append(client)
        return instances

    def data_activewindow(self) -> Dict[str, Any]:
        data = self._send_json("j/activewindow")
        return data or {}

    def data_clients(self) -> list[dict]:
        data = self._send_json("j/clients")
        return data if isinstance(data, list) else []

    def windows_and_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for client in self.data_clients():
            name = client.get("initialClass") or client.get("class") or ""
            if not name:
                continue
            counts[name] = counts.get(name, 0) + 1
        return counts

    def data_monitors(self) -> Dict[int, Dict[str, Any]]:
        raw = self._send_json("j/monitors")
        if not isinstance(raw, list):
            return {}
        monitors: Dict[int, Dict[str, Any]] = {}
        for m in raw:
            mid = m.get("id") or m.get("monitor") or 0
            pos = m.get("position") or m.get("at") or m.get("pos") or m.get("offset")
            size = m.get("size") or m.get("resolution") or m.get("res")
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                mx, my = int(pos[0]), int(pos[1])
            else:
                mx, my = int(m.get("x", 0) or 0), int(m.get("y", 0) or 0)
            if isinstance(size, (list, tuple)) and len(size) >= 2:
                mw, mh = int(size[0]), int(size[1])
            else:
                mw = int(m.get("width", m.get("w", 0)) or 0)
                mh = int(m.get("height", m.get("h", 0)) or 0)
            monitors[int(mid)] = {"x": mx, "y": my, "w": mw, "h": mh, "raw": m}
        return monitors
