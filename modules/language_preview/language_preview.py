from typing import Optional
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.hyprland.service import Hyprland, HyprlandEvent
from fabric.utils import exec_shell_command
from utils import JsonManager
import re
import time
import gi
from gi.repository import GLib  # type: ignore

gi.require_version("Gdk", "3.0")


class LanguagePreview(Window):
    def __init__(
        self,
        replacer: Optional[dict[str, str]] = None,
        position: str = "center",
        margin: str = "40px 40px 40px 40px",
        layer: str = "top",
    ):
        self.json = JsonManager()
        replacer = {"us": "en"}  # short replacements
        self.replacer = {k.lower(): v for k, v in (replacer or {}).items()}

        self.lang_box = Box(
            name="language-preview-box",
            h_expand=True,
            v_expand=True,
            h_align="center",
            v_align="center",
        )
        self.result_box = Box(
            name="language-preview-top",
            h_expand=True,
            v_expand=False,
            h_align="center",
            v_align="center",
        )

        self.items: dict[str, tuple[Box, Label, Label]] = {}

        self.default_fullnames = {
            "us": "English (US)",
            "en": "English",
            "ru": "Russian",
            "uk": "Ukrainian",
            "de": "German",
            "fr": "French",
            "es": "Spanish",
            "it": "Italian",
            "pt": "Portuguese",
            "cn": "Chinese",
            "jp": "Japanese",
        }

        short_raw_list = self._read_layout_raw_list()
        short_codes = [re.sub(r"\W", "", s).lower() for s in short_raw_list]
        self.full_map = self._full_name_map(short_raw_list)

        # build items
        for raw, code in zip(short_raw_list, short_codes):
            display_short = self.replacer.get(code, code)
            short_lbl = Label(label=display_short, name=f"lp-short-{code}")
            full_name = (
                self.full_map.get(code)
                or self.default_fullnames.get(code)
                or raw.strip().replace("_", " ").title()
            )
            full_lbl = Label(label=full_name, name=f"lp-full-{code}")

            wrapper = Box(name=f"lp-item-{code}", orientation="v")
            wrapper.add(short_lbl)
            wrapper.add(full_lbl)

            self.items[code] = (wrapper, short_lbl, full_lbl)
            self.result_box.add(wrapper)

        self.lang_box.add(self.result_box)
        super().__init__(
            name="language-preview",
            margin=margin,
            layer=layer,
            anchor=position,
            h_expand=True,
            v_expand=True,
            v_align="center",
            h_align="center",
            child=self.lang_box,
        )

        self.hypr = Hyprland(commands_only=False)
        self.hypr.connect("event::activelayout", self.on_layout_change)

        self._hide_timeout_id: int | None = None
        self._call_id: int = 0
        self._last_active_value: str | None = None
        self._last_event_ts: float = 0.0
        self._throttle_interval: float = 0.3

        # self.update_active(None)
        self.hide()

    def _run_hyprctl_json(self) -> dict:
        out = exec_shell_command("hyprctl devices -j")
        try:
            return self.json.loads(out)
        except Exception:
            return {}

    def _read_layout_raw_list(self) -> list[str]:
        data = self._run_hyprctl_json()
        try:
            kb = data["keyboards"][0]
        except Exception:
            return []
        layout = kb.get("layout", [])
        if isinstance(layout, list):
            return [str(x) for x in layout]
        else:
            return [s for s in str(layout).split(",") if s]

    def active_language(self) -> str:
        data = self._run_hyprctl_json()
        try:
            kb = data["keyboards"][0]
            return kb.get("active_keymap", "") or ""
        except Exception:
            return ""

    def _full_name_map(self, short_raw_list: list[str]) -> dict[str, str]:
        data = self._run_hyprctl_json()
        try:
            kb = data["keyboards"][0]
        except Exception:
            kb = {}

        short_norm = [re.sub(r"\W", "", s).lower() for s in short_raw_list]

        result: dict[str, str] = {}
        for idx, s in enumerate(short_norm):
            if s in self.default_fullnames:
                result[s] = self.default_fullnames[s]
                continue

            full_list = None
            for field in [
                "layout_names",
                "keymap_names",
                "variant_names",
                "options_names",
            ]:
                val = kb.get(field)
                if isinstance(val, list) and len(val) == len(short_norm):
                    full_list = val
                    break
            if full_list:
                result[s] = str(full_list[idx])
                continue

            active_full = self.active_language()
            active_norm = re.sub(r"\W", "", active_full).lower()
            if s == active_norm or active_norm.startswith(s) or s in active_norm:
                result[s] = active_full
                continue

            raw = short_raw_list[idx] if idx < len(short_raw_list) else s
            result[s] = raw.strip().replace("_", " ").title()

        return result

    def _add_style_class(self, widget, cls: str):
        try:
            widget.add_style_class(cls)
            return
        except Exception:
            pass
        try:
            ctx = widget.get_style_context()
            ctx.add_class(cls)
        except Exception:
            pass

    def _remove_style_class(self, widget, cls: str):
        try:
            widget.remove_style_class(cls)
            return
        except Exception:
            pass
        try:
            ctx = widget.get_style_context()
            ctx.remove_class(cls)
        except Exception:
            pass

    def _set_label_text(self, lbl: Label, text: str):
        try:
            lbl.set_label(text)
            return
        except Exception:
            pass
        try:
            lbl.set_text(text)
            return
        except Exception:
            pass
        try:
            lbl.set_markup(text)
            return
        except Exception:
            pass

    def _score_locale(self, locale_norm: str, active_norm: str) -> int:
        if not locale_norm:
            return 0
        if locale_norm == active_norm:
            return 10000
        if active_norm.startswith(locale_norm) or locale_norm.startswith(active_norm):
            return 100 * len(locale_norm)
        if locale_norm in active_norm or active_norm in locale_norm:
            return len(locale_norm)
        return 0

    def update_active(self, active_raw: str | None):
        if active_raw is None:
            active_raw = self.active_language()

        active_norm = re.sub(r"\W", "", (active_raw or "")).lower()
        best_locale, best_score = None, 0
        for locale in self.items.keys():
            score = self._score_locale(locale, active_norm)
            if score > best_score:
                best_locale, best_score = locale, score

        for locale, (wrapper, short_lbl, full_lbl) in self.items.items():
            baseline_full = self.full_map.get(locale)
            if best_locale is not None and locale == best_locale and best_score > 0:
                self._add_style_class(wrapper, "language-preview-is-active")
                self._add_style_class(short_lbl, "language-preview-short-is-active")
                self._add_style_class(full_lbl, "language-preview-full-is-active")
            else:
                self._remove_style_class(wrapper, "language-preview-is-active")
                self._remove_style_class(short_lbl, "language-preview-short-is-active")
                self._remove_style_class(full_lbl, "language-preview-full-is-active")
            if baseline_full:
                self._set_label_text(full_lbl, baseline_full)

    def _delayed_hide_with_id(self, cid: int):
        if cid != self._call_id:
            return False
        try:
            self.hide()
        finally:
            self._hide_timeout_id = None
        return False

    def _schedule_hide(self, timeout_ms: int, cid: int):
        if self._hide_timeout_id:
            try:
                GLib.source_remove(self._hide_timeout_id)
            except Exception:
                pass
            self._hide_timeout_id = None
        tid = GLib.timeout_add(
            timeout_ms, lambda cid=cid: self._delayed_hide_with_id(cid)
        )
        self._hide_timeout_id = tid

    def on_layout_change(self, *args):
        event = next((a for a in reversed(args) if isinstance(a, HyprlandEvent)), None)
        active_value = None
        if event and getattr(event, "data", None):
            if len(event.data) >= 2:
                active_value = event.data[1]
            elif len(event.data) == 1:
                active_value = event.data[0]

        active_norm = (
            re.sub(r"\W", "", str(active_value)).lower() if active_value else None
        )
        now = time.monotonic()
        if (
            active_norm
            and self._last_active_value == active_norm
            and (now - self._last_event_ts) < self._throttle_interval
        ):
            self._call_id += 1
            self._schedule_hide(400, self._call_id)
            return False

        self._last_event_ts = now
        self._last_active_value = (
            active_norm or re.sub(r"\W", "", self.active_language()).lower()
        )

        self._call_id += 1
        self.update_active(
            str(active_value) if active_value else self.active_language()
        )
        self.show_all()
        self._schedule_hide(400, self._call_id)
        return False

    def change_language(self):
        exec_shell_command("hyprctl switchxkblayout current next")
