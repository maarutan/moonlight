#!/usr/bin/env python3
from typing import Callable, List, Tuple, Dict, Any
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
        t = p.lower()
        if t in ("ctrl", "control"):
            mods |= Gdk.ModifierType.CONTROL_MASK
        elif t == "shift":
            mods |= Gdk.ModifierType.SHIFT_MASK
        elif t in ("alt", "mod1"):
            mods |= Gdk.ModifierType.MOD1_MASK
        elif t == "meta":
            mods |= Gdk.ModifierType.META_MASK
        else:
            key = t
    if key is None:
        key = "tab"
    v = Gdk.keyval_from_name(key)
    if v == 0 and key == "tab":
        v = Gdk.KEY_Tab
    return mods, v


def _normalize(raw: List[Tuple[int, int]]):
    res = []
    for mods, keyval in raw:
        if keyval == Gdk.KEY_Tab:
            if mods & Gdk.ModifierType.SHIFT_MASK:
                res.append(
                    {
                        "mods": int(mods & ~Gdk.ModifierType.SHIFT_MASK),
                        "keys": [Gdk.KEY_ISO_Left_Tab],
                    }
                )
            else:
                res.append({"mods": int(mods), "keys": [Gdk.KEY_Tab]})
        else:
            res.append({"mods": int(mods), "keys": [keyval]})
    res.sort(key=lambda x: bin(x["mods"]).count("1"), reverse=True)
    return res


def setup_keybinds(widget: Gtk.Widget, keybinds: str, callback: Callable, debug=False):
    parsed = _normalize([_parse_single(b) for b in keybinds.split(",") if b.strip()])

    def match(event):
        if debug:
            print(
                f"[KB DBG] keyval={event.keyval} name={Gdk.keyval_name(event.keyval)} raw_state={int(event.state)}"
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
                callback()
            return True
        return False

    def widget_handler(w, e):
        return match(e)

    def top_handler(w, e):
        f = w.get_focus()
        if not f:
            return False
        try:
            if f is not widget and not widget.is_ancestor(f):
                return False
        except:
            return False
        return match(e)

    top = widget.get_toplevel()
    h1 = top.connect("key-press-event", top_handler)
    h2 = widget.connect("key-press-event", widget_handler)
    return (h1, h2)
