from typing import Dict, Optional
from gi.repository import Gio, GLib, GObject  # type: ignore
from loguru import logger
from fabric import Service, Signal  # предполагается что у тебя есть этот базовый класс


class HeadsetService(Service):
    """Dynamic headset battery watcher via UPower (GIO)."""

    @Signal
    def changed(self) -> None:
        """Emitted when any headset battery percentage changes or headsets added/removed."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bus = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
        self.upower_name = "org.freedesktop.UPower"
        self.upower_path = "/org/freedesktop/UPower"
        self.upower_iface = "org.freedesktop.UPower"
        self.device_iface = "org.freedesktop.UPower.Device"

        # key: object_path -> dict(proxy=Gio.DBusProxy, subscription_id=int)
        self._headsets: Dict[str, Dict] = {}

        # listen for new/removed devices on UPower
        # signals DeviceAdded(o) and DeviceRemoved(o)
        self.bus.signal_subscribe(
            self.upower_name,
            self.upower_iface,
            "DeviceAdded",
            self.upower_path,
            None,
            Gio.DBusSignalFlags.NONE,
            self._on_device_added,
        )
        self.bus.signal_subscribe(
            self.upower_name,
            self.upower_iface,
            "DeviceRemoved",
            self.upower_path,
            None,
            Gio.DBusSignalFlags.NONE,
            self._on_device_removed,
        )

        # scan existing devices now
        self._scan_devices()

    def _scan_devices(self) -> None:
        try:
            v = self.bus.call_sync(
                self.upower_name,
                self.upower_path,
                self.upower_iface,
                "EnumerateDevices",
                GLib.Variant("()", ()),
                None,
                Gio.DBusCallFlags.NONE,
                -1,
                None,
            )
            paths = v.unpack()[0]  # <-- ВАЖНО
        except Exception:
            logger.exception("Failed to enumerate UPower devices")
            paths = []

        for p in paths:
            self._maybe_add_device(p)

    def _is_headset_device(self, proxy: Gio.DBusProxy) -> bool:
        # Берём тип, но если Type нет, проверяем Model или Icon
        try:
            tvar = proxy.get_cached_property("Type")
            if tvar is not None:
                dtype = int(tvar.unpack())
                if dtype == 5:
                    return True
            # fallback: проверяем модель/класс устройства
            model_var = proxy.get_cached_property("Model")
            if model_var is not None:
                model = model_var.unpack()
                if "headset" in model.lower() or "ea230" in model.lower():
                    return True
            icon_var = proxy.get_cached_property("IconName")
            if icon_var is not None:
                icon = icon_var.unpack()
                if "headset" in icon.lower():
                    return True
        except Exception:
            return False
        return False

    def _maybe_add_device(self, object_path: str) -> None:
        if object_path in self._headsets:
            return  # already tracked

        try:
            proxy = Gio.DBusProxy.new_sync(
                self.bus,
                Gio.DBusProxyFlags.NONE,
                None,
                self.upower_name,
                object_path,
                self.device_iface,
                None,
            )
        except Exception:
            logger.exception("Failed to create proxy for %s", object_path)
            return

        if not self._is_headset_device(proxy):
            # not a headset
            return

        # subscribe to PropertiesChanged on this device path
        sub_id = self.bus.signal_subscribe(
            self.upower_name,
            "org.freedesktop.DBus.Properties",
            "PropertiesChanged",
            object_path,
            None,
            Gio.DBusSignalFlags.NONE,
            self._on_properties_changed,
        )

        # store proxy + subscription id
        self._headsets[object_path] = {"proxy": proxy, "sub": sub_id}

        logger.debug("Added headset: %s", object_path)
        # emit changed so UI can read initial percentage
        self.emit("changed")

    def _remove_tracked_device(self, object_path: str) -> None:
        info = self._headsets.pop(object_path, None)
        if info:
            try:
                self.bus.signal_unsubscribe(info["sub"])
            except Exception:
                pass
            logger.debug("Removed headset: %s", object_path)
            self.emit("changed")

    # --- D-Bus signal callbacks ---
    def _on_device_added(
        self,
        connection,
        sender_name,
        object_path,
        interface_name,
        signal_name,
        parameters,
    ):
        # parameters is GLib.Variant('(o)', (object_path,))
        try:
            args = parameters.unpack()
            added_path = args[0]
            logger.debug("UPower DeviceAdded: %s", added_path)
            self._maybe_add_device(added_path)
        except Exception:
            logger.exception("Error in DeviceAdded handler")

    def _on_device_removed(
        self,
        connection,
        sender_name,
        object_path,
        interface_name,
        signal_name,
        parameters,
    ):
        try:
            args = parameters.unpack()
            removed_path = args[0]
            logger.debug("UPower DeviceRemoved: %s", removed_path)
            self._remove_tracked_device(removed_path)
        except Exception:
            logger.exception("Error in DeviceRemoved handler")

    def _on_properties_changed(
        self,
        connection,
        sender_name,
        object_path,
        interface_name,
        signal_name,
        parameters,
    ):
        """
        PropertiesChanged signature: (s a{sv} as)
        -> (interface_name, changed_dict, invalidated)
        """
        try:
            iface_name, changed, invalidated = parameters.unpack()
            # changed is a dict mapping string -> GLib.Variant
            if "Percentage" in changed:
                logger.debug("Percentage changed for %s", object_path)
                # emit once for UI to pull the new value
                self.emit("changed")
        except Exception:
            logger.exception("Error in PropertiesChanged handler")

    # --- public helpers ---
    def list_headsets(self) -> Dict[str, float]:
        """Return dict object_path -> percentage (float)."""
        out: Dict[str, float] = {}
        for path, info in self._headsets.items():
            try:
                pvar = info["proxy"].get_cached_property("Percentage")
                if pvar is not None:
                    out[path] = float(pvar.unpack())
                else:
                    out[path] = float("nan")
            except Exception:
                out[path] = float("nan")
        return out

    def first_percentage(self) -> Optional[float]:
        """Convenience: return percentage of the first tracked headset (or None)."""
        for v in self.list_headsets().values():
            if not (isinstance(v, float) and str(v) == "nan"):
                return float(v)
        return None

    def list_headset_names(self) -> Dict[str, str]:
        """Return dict: object_path -> device name/model."""
        out = {}
        for path, info in self._headsets.items():
            proxy = info["proxy"]
            model_var = proxy.get_cached_property("Model")
            name = model_var.unpack() if model_var else path
            out[path] = name
        return out
