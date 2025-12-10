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


from typing import Callable, List, Tuple
from gi.repository import Gdk, Gtk


def _parse_single_keybind(s: str) -> Tuple[int, int]:
    parts = s.strip().replace("+", " ").split()
    mods = 0
    key_name = None

    for p in parts:
        ps = p.lower()
        if ps in ("ctrl", "control"):
            mods |= Gdk.ModifierType.CONTROL_MASK
        elif ps in ("shift",):
            mods |= Gdk.ModifierType.SHIFT_MASK
        elif ps in ("alt", "mod1"):
            mods |= Gdk.ModifierType.MOD1_MASK
        elif ps in ("meta",):
            mods |= Gdk.ModifierType.META_MASK
        else:
            key_name = ps

    if key_name is None:
        key_name = "tab"

    keyval = Gdk.keyval_from_name(key_name)
    if keyval == 0 and key_name in ("tab",):
        keyval = Gdk.KEY_Tab

    return mods, keyval


def setup_keybinds(
    widget: Gtk.Widget, keybinds: str, callback: Callable, debug: bool = False
):
    """
    Универсальная функция. Если debug=True — печатает keyval/state при каждом key-press.
    widget должен быть Gtk.Entry (если нужно перехватывать Tab) или любой Gtk.Widget.
    keybinds: "Tab", "shift tab", "ctrl j, ctrl k" и т.п.
    callback: функция(event) или функция().
    """
    MASK_OF_INTEREST = (
        Gdk.ModifierType.CONTROL_MASK
        | Gdk.ModifierType.SHIFT_MASK
        | Gdk.ModifierType.MOD1_MASK
        | Gdk.ModifierType.META_MASK
    )

    binds = [b.strip() for b in keybinds.split(",") if b.strip()]
    parsed: List[Tuple[int, int]] = []
    for b in binds:
        mods, keyval = _parse_single_keybind(b)
        if keyval != 0:
            parsed.append((mods, keyval))

    # более специфичные (с большим числом модификаторов) идут первыми
    parsed.sort(key=lambda t: bin(int(t[0])).count("1"), reverse=True)

    # безопасно получить имя ISO_Left_Tab, если оно есть
    try:
        ISO_LEFT = Gdk.KEY_ISO_Left_Tab
    except Exception:
        ISO_LEFT = None

    def _handler(widget_obj, event):
        # отладка: показываем raw keyval и name + state (включая полные биты)
        if debug:
            try:
                name = Gdk.keyval_name(event.keyval)
            except Exception:
                name = str(event.keyval)
            print(
                f"[KB DBG] keyval={event.keyval} name={name} raw_state={int(event.state)}"
            )

        # отфильтруем по маске интересующих битов (CapsLock/NumLock игнорируем)
        state = int(event.state) & int(MASK_OF_INTEREST)

        for mods, expected_keyval in parsed:
            # проверка keyval — для Tab учитываем два варианта
            if expected_keyval == Gdk.KEY_Tab:
                if ISO_LEFT is not None:
                    key_ok = event.keyval in (Gdk.KEY_Tab, ISO_LEFT)
                else:
                    key_ok = event.keyval == Gdk.KEY_Tab
            else:
                key_ok = event.keyval == expected_keyval

            if not key_ok:
                continue

            # проверяем, что все нужные модификаторы присутствуют
            if (state & mods) != mods:
                # если ожидали никакие модификаторы (mods==0) — это условие верно ((state & 0) == 0)
                continue

            # всё совпало — вызываем callback
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

            # возвращаем True — останавливаем дальнейшую обработку (важно для Entry)
            return True

        return False

    # подключаем точно к переданному виджету — если это Entry, это гарантирует перехват Tab
    handler_id = widget.connect("key-press-event", _handler)
    return handler_id
