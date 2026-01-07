import shlex
import time
from threading import Thread
from typing import TYPE_CHECKING

from fabric.widgets.box import Box
from fabric.widgets.button import Button
from fabric.widgets.svg import Svg
from fabric.widgets.label import Label
from fabric.utils import GLib, idle_add, exec_shell_command_async

from services.network import NetworkService, NM  # type: ignore
from .network_indicator_handler import NetworkIndicatorHandler
from .network_utils import check_internet, setup_cursor_hover, get_network_info_str
from utils.constants import Const

if TYPE_CHECKING:
    from ...bar import StatusBar


class NetworkWidget(Box):
    def __init__(self, statusbar: "StatusBar"):
        super().__init__(
            name="statusbar-network",
            orientation="h",
            h_expand=True,
            v_expand=True,
            v_align="center",
            h_align="center",
        )
        self.confh = statusbar.confh
        self.wifi_enabled = False
        self.ethernet_enabled = False
        self.is_internet_connection = False
        self.wifi_signal = 0
        self.network_service = NetworkService()
        self.indicator_handler = NetworkIndicatorHandler(self)
        self._last_internet_check = 0
        self._internet_cache = True
        self.timeout = self.confh.config_modules["network"]["notify-timeout"]

        self.svg = Svg(
            name="statusbar-network-icon",
            svg_string=self.indicator_handler.icon_handler(),
            size=self.confh.config_modules["network"]["icon-size"],
        )
        self.not_network_label = Label("")
        self.icon_box = Box(
            name="statusbar-network-box",
            children=[self.not_network_label, self.svg],
            orientation="h",
            style_classes="statusbar-network-box-vertical"
            if self.confh.is_vertical()
            else "",
        )
        self.btn = Button(
            name="statusbar-network-button",
            child=self.icon_box,
            on_clicked=self.on_clicked,
            h_expand=False,
            v_expand=False,
            v_align="center",
            h_align="center",
        )
        setup_cursor_hover(self.btn)
        self.add(self.btn)
        self.network_service.device_ready.connect(self._on_device_ready)

    # ---------------- Device Handlers ----------------
    def _on_device_ready(self, *_):
        client = self.network_service._client
        wifi_device = self.network_service.wifi_device._device  # type: ignore
        if not client or not wifi_device:
            return
        client.connect("notify::wireless-enabled", self._wifi_enabled_handler)
        client.connect("notify::primary-connection", self._primary_device_handler)
        client.connect("notify::connectivity", self._internet_connection_handler)
        wifi_device.connect("notify::state", self._device_state_handler)
        wifi_device.connect("notify::active-access-point", self._on_active_ap_change)
        GLib.timeout_add_seconds(3, self._periodic_internet_check)

        # Initial update
        self._wifi_enabled_handler(client, None)
        self._primary_device_handler(client, None)
        self._internet_connection_handler(client, None)
        self._on_active_ap_change(wifi_device)

    def _device_state_handler(self, device, _pspec):
        self._schedule_internet_check()
        self._schedule_update()

    # ---------------- Internet Check ----------------
    def _schedule_internet_check(self):
        def worker():
            now = time.time()
            if now - self._last_internet_check > 2:
                internet = check_internet(timeout=0.5)
                self._internet_cache = internet
                self._last_internet_check = now
            else:
                internet = self._internet_cache
            nm_state = True
            try:
                nm_state = (
                    self.network_service._client.get_connectivity()  # type: ignore
                    != NM.ConnectivityState.NONE
                )
            except Exception:
                nm_state = True

            new_val = internet and nm_state
            if new_val != self.is_internet_connection:
                self.is_internet_connection = new_val
            idle_add(self.buildwidget)

        Thread(target=worker, daemon=True).start()

    def _internet_connection_handler(self, client, _pspec):
        self._schedule_internet_check()

    def _periodic_internet_check(self) -> bool:
        self._schedule_internet_check()
        return True

    # ---------------- WiFi Handlers ----------------
    def _wifi_strength_handler(self, ap):
        self.wifi_signal = ap.get_strength()
        self._schedule_update()

    def _on_active_ap_change(self, device, *_):
        if getattr(self, "_ap_signal", None):
            try:
                self._ap.disconnect(self._ap_signal)
            except Exception:
                pass

        ap = device.get_active_access_point()
        if not ap:
            self.wifi_signal = 0
            self._schedule_update()
            return

        self._ap_signal = ap.connect(
            "notify::strength", lambda *_: self._wifi_strength_handler(ap)
        )
        self._wifi_strength_handler(ap)

    def _wifi_enabled_handler(self, client, _pspec):
        self.wifi_enabled = bool(client.wireless_get_enabled())
        self._schedule_update()

    def _primary_device_handler(self, client, _pspec):
        primary = client.get_primary_connection()
        self.wifi_enabled = False
        self.ethernet_enabled = False
        if primary:
            ctype = primary.get_connection_type()
            if "wireless" in ctype:
                self.wifi_enabled = True
            elif "ethernet" in ctype:
                self.ethernet_enabled = True
        self._schedule_update()

    # ---------------- Network Info ----------------
    def get_ssid(self) -> str:
        return get_network_info_str(self.network_service, "ssid")

    def get_network_info(self) -> str:
        return get_network_info_str(self.network_service)

    # ---------------- UI ----------------
    def on_clicked(self):
        self._schedule_update()
        icon_path = Const.TEMP_DIR / "tmp_wifi.svg"
        icon_path.write_text(self.indicator_handler.icon_handler())
        info_text = self.get_network_info()
        title = "Network Info"
        cmd = (
            f"notify-send {shlex.quote(title)} "
            f"{shlex.quote(info_text)} "
            f"-i {shlex.quote(icon_path.as_posix())} "
            f"-t {shlex.quote(str(self.timeout))} "
            f"-a {shlex.quote(Const.APP_NAME)}"
        )
        exec_shell_command_async(cmd)

    def _schedule_update(self):
        idle_add(self.buildwidget)

    def buildwidget(self):
        self.not_network_label.set_text("" if self.is_internet_connection else "!")
        self.svg.set_from_string(self.indicator_handler.icon_handler())
        try:
            self.btn.set_tooltip_text(f"{self.get_ssid()} ({self.wifi_signal}%)")
        except Exception:
            pass
