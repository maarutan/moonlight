import time
import subprocess
import threading
from typing import Dict, List, Optional
from fabric.core.service import Service, Property, Signal


class AudioStatusProvider(Service):
    status = Property(type=str, default_value="unknown")
    changed = Signal(name="changed")
    micro = Property(type=bool, default_value=False)
    micro_changed = Signal(name="micro-changed")

    def __init__(
        self,
        debounce_ms: int = 500,
        poll_interval: float = 3.0,
        use_live_test: bool = False,
    ):
        super().__init__()
        self._lock = threading.Lock()
        self._stop = False
        self._subscribe_proc = None
        self._debounce_ms = int(debounce_ms)
        self._poll_interval = float(poll_interval)
        self._use_live_test = bool(use_live_test)
        self._last_live_test = {}
        self._live_test_cooldown = 5.0
        try:
            self.status = self._get_default_sink_type()
        except Exception:
            self.status = "unknown"
        self.micro = False
        self._thread = threading.Thread(target=self._main_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop = True
        try:
            if self._subscribe_proc:
                try:
                    self._subscribe_proc.kill()
                except Exception:
                    pass
        except Exception:
            pass
        try:
            self._thread.join(timeout=1.0)
        except Exception:
            pass

    def _main_loop(self) -> None:
        sub = None
        try:
            sub = subprocess.Popen(
                ["pactl", "subscribe"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            self._subscribe_proc = sub
        except Exception:
            sub = None
        last_snapshot_time = 0.0
        while not self._stop:
            triggered = False
            if sub and sub.stdout:
                try:
                    line = sub.stdout.readline()
                    if line:
                        l = line.lower()
                        if "sink" in l or "source" in l or "card" in l or "server" in l:
                            triggered = True
                    else:
                        triggered = False
                except Exception:
                    triggered = False
            now = time.time()
            if not triggered and now - last_snapshot_time >= self._poll_interval:
                triggered = True
            if triggered:
                last_snapshot_time = now
                sinks = self._parse_pactl_sinks()
                sources = self._parse_pactl_sources()
                new_status, new_micro = self._compute_state_from_snapshot(
                    sinks, sources
                )
                with self._lock:
                    status_changed = new_status != self.status
                    micro_changed = new_micro != self.micro
                if status_changed or micro_changed:
                    debounce_until = time.time() + (self._debounce_ms / 1000.0)
                    stable = True
                    while time.time() < debounce_until and not self._stop:
                        time.sleep(0.06)
                        sinks2 = self._parse_pactl_sinks()
                        sources2 = self._parse_pactl_sources()
                        s2, m2 = self._compute_state_from_snapshot(sinks2, sources2)
                        if s2 != new_status or m2 != new_micro:
                            stable = False
                            break
                    if stable:
                        with self._lock:
                            if status_changed:
                                self.status = new_status
                                try:
                                    self.emit("changed")
                                except Exception:
                                    pass
                            if micro_changed:
                                self.micro = new_micro
                                try:
                                    self.emit("micro-changed")
                                except Exception:
                                    pass
            if not triggered:
                time.sleep(0.1)

    def run_cmd(self, cmd: List[str]) -> str:
        try:
            return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
        except Exception:
            return ""

    def _get_default_sink_name(self) -> Optional[str]:
        out = self.run_cmd(["pactl", "info"])
        for line in out.splitlines():
            line = line.strip()
            if line.lower().startswith("default sink:"):
                return line.split(":", 1)[1].strip()
        return None

    def _parse_pactl_sinks(self) -> Dict[str, Dict]:
        out = self.run_cmd(["pactl", "list", "sinks"])
        sinks: Dict[str, Dict] = {}
        cur = None
        props = {}
        active_port = ""
        in_props = False
        ports = {}
        for raw in out.splitlines():
            line = raw
            stripped = line.strip()
            if stripped.lower().startswith("name:"):
                if cur:
                    sinks[cur] = {
                        "active_port": active_port or "",
                        "props": props,
                        "ports": ports,
                    }
                cur = stripped.split(":", 1)[1].strip()
                props = {}
                active_port = ""
                in_props = False
                ports = {}
                continue
            if cur is None:
                continue
            if stripped.lower().startswith("active port:"):
                active_port = stripped.split(":", 1)[1].strip()
                continue
            if stripped.lower().startswith("properties:"):
                in_props = True
                continue
            if in_props and line and line[0].isspace() and "=" in line:
                left, right = line.strip().split("=", 1)
                props[left.strip()] = right.strip().strip('"')
                continue
            if stripped.lower().startswith("ports:"):
                parm = True
            if (
                stripped
                and ":" in stripped
                and ("available" in stripped.lower() or "type:" in stripped.lower())
            ):
                pass
        if cur:
            sinks[cur] = {
                "active_port": active_port or "",
                "props": props,
                "ports": ports,
            }
        return sinks

    def _parse_pactl_sources(self) -> Dict[str, Dict]:
        out = self.run_cmd(["pactl", "list", "sources"])
        sources: Dict[str, Dict] = {}
        cur = None
        props = {}
        in_props = False
        state = "UNKNOWN"
        active_port = ""
        ports = []
        port_details = {}
        in_ports = False
        for raw in out.splitlines():
            line = raw
            stripped = line.strip()
            if stripped.lower().startswith("source #"):
                cur = None
                props = {}
                in_props = False
                in_ports = False
                active_port = ""
                state = "UNKNOWN"
                ports = []
                port_details = {}
                continue
            if stripped.lower().startswith("name:"):
                if cur:
                    sources[cur] = {
                        "props": props,
                        "state": state,
                        "active_port": active_port,
                        "ports": ports,
                        "port_details": port_details,
                    }
                cur = stripped.split(":", 1)[1].strip()
                props = {}
                in_props = False
                in_ports = False
                active_port = ""
                state = "UNKNOWN"
                ports = []
                port_details = {}
                continue
            if cur is None:
                continue
            if stripped.lower().startswith("state:"):
                state = stripped.split(":", 1)[1].strip().upper()
                in_props = False
                in_ports = False
                continue
            if stripped.lower().startswith("active port:"):
                active_port = stripped.split(":", 1)[1].strip()
                in_props = False
                in_ports = False
                continue
            if stripped.lower().startswith("properties:"):
                in_props = True
                in_ports = False
                continue
            if stripped.lower().startswith("ports:"):
                in_ports = True
                in_props = False
                continue
            if stripped.lower().startswith("formats:"):
                in_ports = False
                in_props = False
                continue
            if in_props and line and line[0].isspace() and "=" in line:
                left, right = line.strip().split("=", 1)
                props[left.strip()] = right.strip().strip('"')
                continue
            if in_ports and line and line[0].isspace():
                if ":" in line:
                    port_line = line.strip()
                    port_name = port_line.split(":", 1)[0].strip()
                    port_info = (
                        port_line.split(":", 1)[1].strip() if ":" in port_line else ""
                    )
                    ports.append(port_name)
                    pi = port_info.lower()
                    availability = "unknown"
                    if "not available" in pi:
                        availability = "no"
                    elif "availability unknown" in pi:
                        availability = "unknown"
                    elif "available" in pi:
                        availability = "yes"
                    port_details[port_name] = {
                        "info": port_info,
                        "availability": availability,
                    }
        if cur:
            sources[cur] = {
                "props": props,
                "state": state,
                "active_port": active_port,
                "ports": ports,
                "port_details": port_details,
            }
        return sources

    def _find_sources_for_sink(
        self, sink_name: str, sinks: Dict[str, Dict], sources: Dict[str, Dict]
    ) -> List[str]:
        sink = sinks.get(sink_name)
        if not sink:
            return []
        sink_props = sink.get("props", {})
        sink_card = (
            sink_props.get("api.alsa.card")
            or sink_props.get("alsa.card")
            or sink_props.get("device.string")
        )
        sink_node = sink_props.get("node.name", "")
        sink_prefix = sink_node.split(".", 1)[0] if sink_node else ""
        sink_bus_id = (sink_props.get("device.bus-id") or "").lower()
        sink_serial = (sink_props.get("device.serial") or "").lower()
        sink_devname = (sink_props.get("device.name") or "").lower()
        matched: List[str] = []
        for src_name, src_data in sources.items():
            if src_name.endswith(".monitor"):
                continue
            src_props = src_data.get("props", {})
            src_card = (
                src_props.get("api.alsa.card")
                or src_props.get("alsa.card")
                or src_props.get("device.string")
            )
            src_node = src_props.get("node.name", "")
            src_prefix = src_node.split(".", 1)[0] if src_node else ""
            src_bus_id = (src_props.get("device.bus-id") or "").lower()
            src_serial = (src_props.get("device.serial") or "").lower()
            src_devname = (src_props.get("device.name") or "").lower()
            if sink_card and src_card and sink_card == src_card:
                matched.append(src_name)
                continue
            if sink_prefix and src_prefix and sink_prefix == src_prefix:
                matched.append(src_name)
                continue
            if sink_bus_id and src_bus_id and sink_bus_id == src_bus_id:
                matched.append(src_name)
                continue
            if sink_serial and src_serial and sink_serial == src_serial:
                matched.append(src_name)
                continue
            if sink_devname and src_devname and sink_devname == src_devname:
                matched.append(src_name)
                continue
            if (
                "usb" in (sink_props.get("device.bus", "") or "").lower()
                and "usb" in (src_props.get("device.bus", "") or "").lower()
            ):
                matched.append(src_name)
                continue
        return matched

    def _source_has_signal(self, source_name: str, duration: float = 0.8) -> bool:
        cmd = ["parec", "--device=" + source_name, "--raw"]
        try:
            proc = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=duration
            )
            data = proc.stdout or b""
            return any(b != 0 for b in data)
        except Exception:
            return False

    def _detect_sink_type_from_props(self, sink_name: str, sink_data: Dict) -> str:
        props = sink_data.get("props", {})
        node = (props.get("node.name") or "").lower()
        desc = (props.get("device.description") or "").lower()
        bus = (props.get("device.bus") or "").lower()
        if "usb" in bus or node.startswith("alsa_output.usb") or "usb" in node:
            return "usb"
        if "bluez" in node or "bluetooth" in desc:
            return "bluetooth"
        if (
            "hdmi" in node
            or "displayport" in node
            or "hdmi" in desc
            or "displayport" in desc
        ):
            return "hdmi"
        port = (sink_data.get("active_port") or "").lower()
        if any(k in port for k in ("headphone", "headset", "analog")):
            return "aux"
        if "analog" in node or "analog" in desc or "jack" in node or "jack" in desc:
            return "aux"
        return "unknown"

    def _compute_state_from_snapshot(
        self, sinks: Dict[str, Dict], sources: Dict[str, Dict]
    ) -> (str, bool):
        default = self._get_default_sink_name()
        if not default:
            return "unknown", False
        sink = sinks.get(default, {})
        device_type = (
            self._detect_sink_type_from_props(default, sink) if sink else "unknown"
        )
        mic_present = False
        if device_type == "usb":
            candidates = self._find_sources_for_sink(default, sinks, sources)
            for s in candidates:
                if s.endswith(".monitor"):
                    continue
                p = sources.get(s, {}).get("props", {})
                node = (p.get("node.name") or "").lower()
                bus = (p.get("device.bus") or "").lower()
                if "usb" in bus or "usb" in node:
                    mic_present = True
                    break
        elif device_type == "bluetooth":
            candidates = self._find_sources_for_sink(default, sinks, sources)
            for s in candidates:
                p = sources.get(s, {}).get("props", {})
                node = (p.get("node.name") or "").lower()
                desc = (p.get("device.description") or "").lower()
                if "bluez" in node or "bluetooth" in desc:
                    mic_present = True
                    break
        elif device_type == "aux":
            sink_ports = sink.get("props", {})
            active_out = (sink.get("active_port") or "").lower()
            candidates = self._find_sources_for_sink(default, sinks, sources)
            for s in candidates:
                src = sources.get(s, {})
                active_in = (src.get("active_port") or "").lower()
                ports = src.get("ports", [])
                port_details = src.get("port_details", {})
                if (
                    "headset-mic" in active_in
                    or "headset" in active_in
                    or "mic" in active_in
                ):
                    pd = port_details.get(active_in, {})
                    if pd.get("availability") != "no":
                        mic_present = True
                        break
                for p in ports:
                    pl = p.lower()
                    if (
                        "headset" in pl
                        or "mic" in pl
                        or "headphone" in pl
                        or "input" in pl
                    ):
                        pd = port_details.get(p, {})
                        if pd.get("availability") == "no":
                            continue
                        if pd.get("availability") == "yes":
                            mic_present = True
                            break
                        if self._use_live_test:
                            last = self._last_live_test.get(s, 0)
                            if time.time() - last >= self._live_test_cooldown:
                                self._last_live_test[s] = time.time()
                                if self._source_has_signal(s, duration=0.8):
                                    mic_present = True
                                    break
                if mic_present:
                    break
        else:
            mic_present = False
        return device_type, bool(mic_present)

    def _get_default_sink_type(self) -> str:
        default = self._get_default_sink_name()
        if not default:
            return "unknown"
        sinks = self._parse_pactl_sinks()
        data = sinks.get(default)
        if not data:
            return "unknown"
        return self._detect_sink_type_from_props(default, data)
