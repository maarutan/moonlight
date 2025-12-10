import os
import ctypes
import ctypes.util

import gi

from utils.constants import Const

gi.require_version("Pango", "1.0")
from gi.repository import Pango, Gio, Gtk  # type: ignore

_libname = ctypes.util.find_library("fontconfig")
if not _libname:
    raise RuntimeError("Не найдена библиотека fontconfig (установите её).")
_fc = ctypes.CDLL(_libname)

if hasattr(_fc, "FcInit"):
    _fc.FcInit()
_fc.FcConfigGetCurrent.restype = ctypes.c_void_p
_fc.FcConfigAppFontAddFile.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
_fc.FcConfigAppFontAddFile.restype = ctypes.c_int  # возвращает FcBool


def _register_font_with_fontconfig(path: str) -> bool:
    cfg = _fc.FcConfigGetCurrent()
    res = _fc.FcConfigAppFontAddFile(cfg, path.encode("utf-8"))
    return bool(res)


def load_fonts_from_dir():
    path = Const.FONT_DIR_ASSETS.as_posix()
    gfile = Gio.File.new_for_path(path)
    try:
        enumerator = gfile.enumerate_children(
            "standard::name,standard::type", Gio.FileQueryInfoFlags.NONE, None
        )
    except Exception as e:
        raise RuntimeError(f"Failed to enumerate {path}: {e}")

    font_exts = {".ttf", ".ttc", ".otf", ".woff", ".woff2"}
    added = []
    while True:
        info = enumerator.next_file(None)
        if info is None:
            break
        if info.get_file_type() == Gio.FileType.REGULAR:
            child = enumerator.get_child(info)
            font_path = child.get_path()
            _, ext = os.path.splitext(font_path or "")
            if ext.lower() in font_exts:
                ok = _register_font_with_fontconfig(font_path)  # type: ignore
                if ok:
                    added.append(font_path)
    enumerator.close(None)
    return added
