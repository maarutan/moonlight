import time
from threading import Thread
from fabric.utils import idle_add
from utils.widget_utils import check_internet


def setup_cursor_hover(widget):
    from utils.widget_utils import setup_cursor_hover as fn

    fn(widget)


def get_network_info_str(network_service, field=None):
    """
    Возвращает информацию о сети. Если field="ssid", возвращает только SSID.
    """
    ssid = "not connected"
    signal = 0
    bssid = "N/A"
    frequency = "N/A"
    security = "N/A"
    internet = "Unknown"
    ip_address = "N/A"
    speed = "N/A"

    wifi = network_service.wifi_device
    client = getattr(network_service, "_client", None)

    if wifi and getattr(wifi, "_ap", None):
        ap = wifi._ap
        if ap:
            ssid_bytes = ap.get_ssid().get_data() if ap.get_ssid() else b""
            ssid = ssid_bytes.decode("utf-8") if ssid_bytes else "Unknown"
            try:
                signal = int(ap.get_strength())
            except Exception:
                signal = 0
            try:
                bssid = ap.get_bssid() or "N/A"
            except Exception:
                bssid = "N/A"
            try:
                frequency = f"{ap.get_frequency()} MHz"
            except Exception:
                frequency = "N/A"
            try:
                security = wifi.get_ap_security(ap)
            except Exception:
                security = "N/A"

    if field == "ssid":
        return ssid

    try:
        if client is not None:
            conn = None
            if wifi and getattr(wifi, "_device", None):
                try:
                    conn = wifi._device.get_active_connection()
                except Exception:
                    conn = None
            if conn:
                try:
                    state = conn.get_state()
                    internet = "Yes" if state == 1 else "No"
                except Exception:
                    internet = "Unknown"
                try:
                    ip4 = conn.get_ip4_config()
                    if ip4 and ip4.get_addresses():
                        addr = ip4.get_addresses()[0]
                        ip_address = (
                            addr.get_address()
                            if hasattr(addr, "get_address")
                            else str(addr)
                        )
                except Exception:
                    ip_address = "N/A"
            try:
                dev = wifi._device if wifi and getattr(wifi, "_device", None) else None
                if dev and hasattr(dev, "get_speed"):
                    sp = dev.get_speed()
                    if sp:
                        speed = f"{sp} Mbps"
            except Exception:
                speed = "N/A"
    except Exception:
        pass

    info = (
        f"Name: {ssid}\n"
        f"Signal: {signal}%\n"
        f"BSSID: {bssid}\n"
        f"Frequency: {frequency}\n"
        f"Security: {security}\n"
        f"Internet: {internet}\n"
        f"IP: {ip_address}\n"
        f"Speed: {speed}"
    )
    return info
