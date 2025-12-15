from typing import (
    Any,
    Literal,
    Optional,
    Callable,
    Tuple,
)
from fabric.utils import Gtk, bulk_connect, Gdk


def setup_cursor_hover(
    widget,
    cursor_name: Literal["pointer", "crosshair", "grab"] = "pointer",
) -> None:
    display = Gdk.Display.get_default()
    cursor = Gdk.Cursor.new_from_name(display, cursor_name)  # type:ignore

    if cursor is None:
        return

    def _set_cursor(w, cur):
        win = w.get_window()
        if win is not None:
            win.set_cursor(cur)

    def on_enter_notify_event(w, _event):
        _set_cursor(w, cursor)
        return False

    def on_leave_notify_event(w, _event):
        _set_cursor(w, None)
        return False

    bulk_connect(
        widget,
        {
            "enter-notify-event": on_enter_notify_event,
            "leave-notify-event": on_leave_notify_event,
        },
    )


def merge(base: dict, override: dict) -> dict:
    result = base.copy()
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge(result[key], value)
        else:
            result[key] = value
    return result


def bar_margin_handler(
    position: str,
    layout_config: str,
    default_value: Any,
    widget_name: str,
    px: int = 30,
) -> str:
    section: Optional[str] = None
    for sec_name, widgets in layout_config.items():  # type: ignore
        for w in widgets:
            if isinstance(w, str) and widget_name in w:
                section = sec_name
                break

    px = 30
    m = f"{px}px"

    margin = {
        "start": {
            "top": f"{m} 0 {m} {m}",
            "bottom": f"{m} 0 {m} {m}",
            "left": f"{m} {m} 0 {m}",
            "right": f"{m} {m} 0 {m}",
        },
        "center": {
            "top": f"0 0 {m} 0",
            "bottom": f"{m} 0 0 0",
            "left": f"{m} {m} {m} {m}",
            "right": f"{m} {m} {m} {m}",
        },
        "end": {
            "top": f"0 {m} {m} 0",
            "bottom": f"{m} {m} 0 0",
            "left": f"{m} 0 {m} {m}",
            "right": f"{m} {m} {m} 0",
        },
    }

    return margin.get(section, {}).get(  # type: ignore
        position,
        default_value,
    )


def bar_anchor_handler(
    widget_name: str,
    position: str,
    layout_config: dict,
    default_value: Any,
) -> str:
    section: Optional[str] = None
    for sec_name, widgets in layout_config.items():
        if any(isinstance(w, str) and widget_name in w for w in widgets):
            section = sec_name
            break

    anchors = {
        "start": {
            "top": "top left",
            "bottom": "bottom left",
            "left": "top left",
            "right": "top right",
        },
        "center": {
            "top": "top center",
            "bottom": "bottom center",
            "left": "center left",
            "right": "center right",
        },
        "end": {
            "top": "top right",
            "bottom": "bottom right",
            "left": "bottom left",
            "right": "bottom right",
        },
    }

    return anchors.get(section, {}).get(  # type: ignore
        position,
        default_value,
    )


from typing import Callable, List, Tuple, Dict, Any, Optional
from fabric.utils import Gdk, Gtk

MASKS = (
    Gdk.ModifierType.CONTROL_MASK
    | Gdk.ModifierType.SHIFT_MASK
    | Gdk.ModifierType.MOD1_MASK
    | Gdk.ModifierType.META_MASK
)


def _parse_single(s: str) -> Tuple[int, int]:
    parts = s.strip().replace("+", " ").split()
    mods = 0
    key = None
    for p in parts:
        p = p.lower()
        if p in ("ctrl", "control"):
            mods |= Gdk.ModifierType.CONTROL_MASK
        elif p == "shift":
            mods |= Gdk.ModifierType.SHIFT_MASK
        elif p in ("alt", "mod1"):
            mods |= Gdk.ModifierType.MOD1_MASK
        elif p == "meta":
            mods |= Gdk.ModifierType.META_MASK
        else:
            key = p
    if key is None:
        key = "tab"
    val = Gdk.keyval_from_name(key)
    if val == 0 and key == "tab":
        val = Gdk.KEY_Tab
    return mods, val


def _normalize(raw: List[Tuple[int, int]]) -> List[Dict[str, Any]]:
    try:
        ISO_LEFT = Gdk.KEY_ISO_Left_Tab
    except Exception:
        ISO_LEFT = None
    out: List[Dict[str, Any]] = []
    for mods, keyval in raw:
        if keyval == Gdk.KEY_Tab:
            if mods & Gdk.ModifierType.SHIFT_MASK:
                out.append(
                    {
                        "mods": int(mods & ~Gdk.ModifierType.SHIFT_MASK),
                        "keys": [ISO_LEFT]
                        if ISO_LEFT is not None
                        else [Gdk.KEY_ISO_Left_Tab],
                    }
                )
            else:
                out.append({"mods": int(mods), "keys": [Gdk.KEY_Tab]})
        else:
            out.append({"mods": int(mods), "keys": [keyval]})
    # more specific (more modifier bits) first
    out.sort(key=lambda e: bin(int(e["mods"])).count("1"), reverse=True)
    return out


def _find_top_widget(start) -> Optional[object]:
    try:
        top = start.get_toplevel()
    except Exception:
        top = None
    if top is not None and hasattr(top, "get_focus"):
        return top
    # climb parents to find object with get_focus or a Gtk.Window
    p = start
    while True:
        try:
            parent = p.get_parent()
        except Exception:
            parent = None
        if parent is None:
            break
        if hasattr(parent, "get_focus") or isinstance(parent, Gtk.Window):
            return parent
        p = parent
    return None


def setup_keybinds(
    widget: Gtk.Widget, keybinds: str, callback: Callable, debug: bool = False
):
    parsed = _normalize([_parse_single(b) for b in keybinds.split(",") if b.strip()])

    def _match(event):
        if debug:
            try:
                name = Gdk.keyval_name(event.keyval)
            except Exception:
                name = str(event.keyval)
            print(
                f"[KB DBG] keyval={event.keyval} name={name} raw_state={int(event.state)}"
            )
        state = int(event.state) & int(MASKS)
        for ent in parsed:
            if event.keyval not in ent["keys"]:
                continue
            if (state & ent["mods"]) != ent["mods"]:
                continue
            try:
                callback(event)
            except TypeError:
                try:
                    callback()
                except Exception:
                    pass
            except Exception:
                try:
                    callback()
                except Exception:
                    pass
            return True
        return False

    def _widget_handler(w, event):
        return _match(event)

    def _top_handler(top, event):
        try:
            focused = None
            if hasattr(top, "get_focus"):
                focused = top.get_focus()
        except Exception:
            focused = None
        if focused is None:
            # if we don't know focus, still try to match (safer)
            return _match(event)
        try:
            if focused is not widget and not widget.is_ancestor(focused):
                return False
        except Exception:
            return False
        return _match(event)

    handlers = []
    top_widget = _find_top_widget(widget)
    if top_widget is not None and hasattr(top_widget, "connect"):
        try:
            handlers.append(top_widget.connect("key-press-event", _top_handler))
        except Exception:
            pass
    try:
        handlers.append(widget.connect_after("key-press-event", _widget_handler))
    except Exception:
        try:
            handlers.append(widget.connect("key-press-event", _widget_handler))
        except Exception:
            pass
    return handlers
