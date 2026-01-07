from __future__ import annotations
import time
from fabric.utils.helpers import GLib
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.hyprland.service import Hyprland, HyprlandEvent
from fabric.hyprland.widgets import HyprlandLanguage
from .hypr_state import HyprState
from .config import ConfigHandlerLanguagePreview

config_handler = ConfigHandlerLanguagePreview()

if not config_handler.config["enabled"]:
    LanguagePreview = None  # type: ignore
else:

    class LanguagePreview(Window):
        EVENT_THROTTLE_SEC = 0.3
        ACTIVE_CLASSES = {
            "active": {
                "wrapper": "language-preview-wrapper-is-active",
                "short": "language-preview-short-is-active",
                "full": "language-preview-full-is-active",
            },
            "wrapper": "language-preview-wrapper",
            "short": "language-preview-short",
            "full": "language-preview-full",
        }

        def __init__(self):
            self.confh = config_handler
            self.default_fullnames = self.confh.config["default-fullnames"]
            self.replacer = {
                k.lower(): v for k, v in (self.confh.config["replacer"] or {}).items()
            }
            self.hypr = Hyprland()
            self.hypr_language = HyprlandLanguage()
            self.state = HyprState(self.hypr)
            self._hide_timeout_id: int | None = None
            self._call_id: int = 0
            self._last_active_value: str | None = None
            self._last_event_ts: float = 0.0
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
            short_raw_list = self.state.get_layouts()
            short_codes = [self.state.norm(s) for s in short_raw_list]
            self.full_map = self.state.build_fullname_map(
                short_raw_list, self.default_fullnames
            )
            for raw, code in zip(short_raw_list, short_codes):
                short_text = self.replacer.get(code, code)
                short_lbl = Label(label=short_text, name=f"lp-short-{code}")
                pretty_fallback = raw.strip().replace("_", " ").title()
                full_text = (
                    self.full_map.get(code)
                    or self.default_fullnames.get(code)
                    or pretty_fallback
                )
                full_lbl = Label(label=full_text, name=f"lp-full-{code}")
                wrapper = Box(name=f"lp-item-{code}", orientation="v")
                wrapper.add(short_lbl)
                wrapper.add(full_lbl)
                self.items[code] = (wrapper, short_lbl, full_lbl)
                self.result_box.add(wrapper)
            self.lang_box.add(self.result_box)
            super().__init__(
                name="language-preview",
                margin=self.confh.config["margin"],
                layer=self.confh.config["layer"],
                anchor=self.confh.config["anchor"],
                h_expand=True,
                v_expand=True,
                v_align="center",
                h_align="center",
                child=self.lang_box,
            )
            self.hypr_language.layout_changed.connect(self.on_layout_change)
            # self.hypr_language.connect("notify::language", self.on_layout_change)
            self.hide()

        def _set_label_text(self, lbl: Label, text: str) -> None:
            for setter in (
                getattr(lbl, "set_label", None),
                getattr(lbl, "set_text", None),
                getattr(lbl, "set_markup", None),
            ):
                if callable(setter):
                    try:
                        setter(text)
                        return
                    except Exception:
                        continue

        def _rebuild_items(self) -> None:
            try:
                for child in list(self.result_box.get_children()):
                    self.result_box.remove(child)
            except Exception:
                for child in list(self.result_box):
                    self.result_box.remove(child)

            self.items = {}

            short_raw_list = self.state.get_layouts()
            short_codes = [self.state.norm(s) for s in short_raw_list]
            self.full_map = self.state.build_fullname_map(
                short_raw_list, self.default_fullnames
            )

            for raw, code in zip(short_raw_list, short_codes):
                short_text = self.replacer.get(code, code)

                short_lbl = Label(label=short_text, name=f"lp-short-{code}")

                pretty_fallback = raw.strip().replace("_", " ").title()
                full_text = (
                    self.full_map.get(code)
                    or self.default_fullnames.get(code)
                    or pretty_fallback
                )
                full_lbl = Label(label=full_text, name=f"lp-full-{code}")

                wrapper = Box(name=f"lp-item-{code}", orientation="v")
                wrapper.add(short_lbl)
                wrapper.add(full_lbl)

                self.items[code] = (wrapper, short_lbl, full_lbl)
                self.result_box.add(wrapper)

        def _add_class(self, widget, cls: str) -> None:
            if hasattr(widget, "add_style_class"):
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

        def _remove_class(self, widget, cls: str) -> None:
            if hasattr(widget, "remove_style_class"):
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

        def _apply_active_state(
            self, widgets: tuple[Box, Label, Label], active: bool
        ) -> None:
            wrapper, short_lbl, full_lbl = widgets
            classes = self.ACTIVE_CLASSES
            if active:
                self._remove_class(wrapper, classes["active"]["wrapper"])
                self._remove_class(short_lbl, classes["active"]["short"])
                self._remove_class(full_lbl, classes["active"]["full"])

                # ------------ _ active
                self._add_class(wrapper, classes["active"]["wrapper"])
                self._add_class(short_lbl, classes["active"]["short"])
                self._add_class(full_lbl, classes["active"]["full"])
            else:
                self._remove_class(wrapper, classes["active"]["wrapper"])
                self._remove_class(short_lbl, classes["active"]["short"])
                self._remove_class(full_lbl, classes["active"]["full"])
                # ------------ not _ active
                self._add_class(wrapper, classes["wrapper"])
                self._add_class(short_lbl, classes["short"])
                self._add_class(full_lbl, classes["full"])

        def _score_locale(self, locale_norm: str, active_norm: str) -> int:
            if not locale_norm:
                return 0

            alias = self.confh.config["alias"]

            alias_norm = alias.get(locale_norm, "")

            def match(a: str, b: str) -> int:
                if a == b:
                    return 10000
                if b.startswith(a) or a.startswith(b):
                    return 100 * len(a)
                if a in b or b in a:
                    return len(a)
                return 0

            base_score = match(locale_norm, active_norm)
            alias_score = match(alias_norm, active_norm) if alias_norm else 0

            return max(base_score, alias_score)

        def update_active(self, active_raw: str | None) -> None:
            current_layouts_raw = self.state.get_layouts()
            current_layouts_norm = [self.state.norm(s) for s in current_layouts_raw]

            if set(current_layouts_norm) != set(self.items.keys()):
                self._rebuild_items()

            current_full = active_raw or self.state.get_active_keymap()
            current_norm = self.state.norm(current_full)

            best_locale = None
            best_score = 0
            for locale_code in self.items.keys():
                sc = self._score_locale(locale_code, current_norm)
                if sc > best_score:
                    best_locale, best_score = locale_code, sc

            for locale_code, widgets in self.items.items():
                baseline_full = self.full_map.get(locale_code)
                if baseline_full:
                    self._set_label_text(widgets[2], baseline_full)

                is_active = (
                    best_locale is not None
                    and locale_code == best_locale
                    and best_score > 0
                )

                self._apply_active_state(widgets, is_active)

        def _hide_later_if_same_call(self, cid: int) -> bool:
            if cid == self._call_id:
                try:
                    self.hide()
                finally:
                    self._hide_timeout_id = None
            return False

        def _schedule_hide(self, delay_ms: int) -> None:
            if self._hide_timeout_id:
                try:
                    GLib.source_remove(self._hide_timeout_id)
                except Exception:
                    pass
                self._hide_timeout_id = None
            cid = self._call_id
            self._hide_timeout_id = GLib.timeout_add(
                delay_ms, lambda cid=cid: self._hide_later_if_same_call(cid)
            )

        def on_layout_change(self, *args):
            if len(args) >= 2:
                active_value = args[1]
            else:
                active_value = None

            now = time.monotonic()
            active_norm = self.state.norm(active_value if active_value else "")

            if (
                active_norm
                and self._last_active_value == active_norm
                and (now - self._last_event_ts) < self.EVENT_THROTTLE_SEC
            ):
                self._call_id += 1
                self._schedule_hide(self.confh.config["hide-delay"])
                return False

            self._last_event_ts = now
            self._last_active_value = active_norm or self.state.norm(
                self.state.get_active_keymap()
            )

            self._call_id += 1
            self.update_active(active_value or None)
            self.show_all()
            self._schedule_hide(self.confh.config["hide-delay"])
            return False
