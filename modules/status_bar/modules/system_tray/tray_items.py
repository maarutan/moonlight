#!/usr/bin/env python3
from fabric.widgets.button import Button
import gi
import logging
import re
from pathlib import Path
from typing import Optional, Dict, Any
from config import RESOLVED_ICONS
from utils import IconResolver, WINDOW_TITLE_MAP
from fabric.system_tray.service import SystemTrayItem, SystemTray, SystemTrayItem
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib  # type: ignore
from fabric.widgets.box import Box
from fabric.widgets.grid import Grid

from utils.widget_utils import setup_cursor_hover

logger = logging.getLogger(__name__)


class TrayItems(Box):
    def __init__(
        self,
        orientation_pos: bool = True,
        pixel_size: int = 20,
        refresh_interval: int = 1,
        grid: bool = True,
        spacing: int = 8,
        **kwargs,
    ) -> None:
        orientation = (
            Gtk.Orientation.HORIZONTAL if orientation_pos else Gtk.Orientation.VERTICAL
        )
        self.icon_resolver = IconResolver(Path(RESOLVED_ICONS))
        super().__init__(
            name="systray", orientation=orientation, spacing=spacing, **kwargs
        )
        self.enabled = True
        super().set_visible(False)
        self.grid_enabled = grid
        self.pixel_size = pixel_size
        self.refresh_interval = refresh_interval
        self.buttons_by_id: Dict[str, Gtk.Button] = {}
        self.items_by_id: Dict[str, Any] = {}
        self.grid_layout = (
            Grid(row_spacing=8, column_spacing=8) if self.grid_enabled else None
        )
        if self.grid_layout:
            self.add(self.grid_layout)
        if SystemTray is not None:
            try:
                self.tray = SystemTray()
            except Exception as e:
                logger.warning("SystemTray init failed: %s", e)
                self.tray = None
        else:
            logger.warning("SystemTray class not available; tray will be inactive.")
            self.tray = None
        GLib.timeout_add_seconds(max(1, int(self.refresh_interval)), self._poll_tray)
        self.show_all()

    def _find_window_map_entry(self, app_id_or_name: str) -> Optional[list]:
        if not app_id_or_name:
            return None
        aid = app_id_or_name.lower()
        for entry in WINDOW_TITLE_MAP:
            try:
                key = (entry[0] or "").lower()
            except Exception:
                continue
            if not key:
                continue
            if key == aid or key in aid:
                return entry
        regex_chars = set(".^$*+?[](){}|\\")
        for entry in WINDOW_TITLE_MAP:
            key = entry[0] or ""
            if any(ch in regex_chars for ch in key):
                try:
                    if re.search(key, app_id_or_name, re.IGNORECASE):
                        return entry
                except re.error:
                    continue
        return None

    def _glyph_for_item(self, item: Any) -> Optional[str]:
        try:
            ident = getattr(item, "identifier", None) or getattr(item, "id", None) or ""
            if ident:
                e = self._find_window_map_entry(str(ident))
                if e:
                    return e[1]
        except Exception:
            pass
        try:
            name = getattr(item, "icon_name", None)
            if callable(name):
                try:
                    name = name()
                except Exception:
                    name = None
            if isinstance(name, str):
                e = self._find_window_map_entry(name)
                if e:
                    return e[1]
        except Exception:
            pass
        try:
            title = getattr(item, "title", None)
            if callable(title):
                try:
                    title = title()
                except Exception:
                    title = None
            if isinstance(title, str):
                e = self._find_window_map_entry(title)
                if e:
                    return e[1]
        except Exception:
            pass
        probe = None
        try:
            probe = (
                getattr(item, "identifier", None)
                or getattr(item, "icon_name", None)
                or ""
            )
        except Exception:
            probe = ""
        if probe:
            try:
                resolved = self.icon_resolver.get_icon_name(str(probe))
                e = self._find_window_map_entry(resolved)
                if e:
                    return e[1]
            except Exception:
                pass
        return None

    def _get_item_pixbuf(self, item: Any) -> GdkPixbuf.Pixbuf | None:
        try:
            try:
                if hasattr(item, "get_preferred_icon_pixbuf"):
                    pix = item.get_preferred_icon_pixbuf(self.pixel_size)
                    if pix is not None:
                        return pix
            except Exception:
                pass
            try:
                pixmap = getattr(item, "icon_pixmap", None)
                if pixmap is not None and hasattr(pixmap, "as_pixbuf"):
                    try:
                        pix = pixmap.as_pixbuf(self.pixel_size)
                        if pix is not None:
                            return pix
                    except Exception:
                        pass
            except Exception:
                pass
            try:
                icon_name = getattr(item, "icon_name", None)
                if callable(icon_name):
                    try:
                        icon_name = icon_name()
                    except Exception:
                        icon_name = None
                if isinstance(icon_name, str) and icon_name:
                    try:
                        theme = getattr(item, "icon_theme", None)
                        if callable(theme):
                            try:
                                theme = theme()
                            except Exception:
                                theme = None
                        if isinstance(theme, Gtk.IconTheme):
                            if theme.has_icon(icon_name):
                                try:
                                    return theme.load_icon(
                                        icon_name,
                                        self.pixel_size,
                                        Gtk.IconLookupFlags.FORCE_SIZE,
                                    )
                                except Exception:
                                    pass
                        else:
                            gtheme = Gtk.IconTheme.get_default()
                            if gtheme.has_icon(icon_name):
                                try:
                                    return gtheme.load_icon(
                                        icon_name,
                                        self.pixel_size,
                                        Gtk.IconLookupFlags.FORCE_SIZE,
                                    )
                                except Exception:
                                    pass
                    except Exception:
                        pass
            except Exception:
                pass
            probe_id = None
            try:
                probe_id = (
                    getattr(item, "identifier", None)
                    or getattr(item, "id", None)
                    or getattr(item, "icon_name", None)
                    or ""
                )
                if callable(probe_id):
                    try:
                        probe_id = probe_id()
                    except Exception:
                        probe_id = ""
                probe_id = str(probe_id)
            except Exception:
                probe_id = ""
            if probe_id:
                try:
                    resolved = self.icon_resolver.get_icon_name(probe_id)
                    if resolved and resolved != self.icon_resolver.default_icon:
                        try:
                            gtheme = Gtk.IconTheme.get_default()
                            if gtheme.has_icon(resolved):
                                try:
                                    return gtheme.load_icon(
                                        resolved,
                                        self.pixel_size,
                                        Gtk.IconLookupFlags.FORCE_SIZE,
                                    )
                                except Exception:
                                    pass
                        except Exception:
                            pass
                        try:
                            pix = self.icon_resolver.get_icon_pixbuf(
                                probe_id, size=self.pixel_size
                            )
                            if pix is not None:
                                return pix
                        except Exception:
                            pass
                except Exception:
                    try:
                        pix = self.icon_resolver.get_icon_pixbuf(
                            probe_id, size=self.pixel_size
                        )
                        if pix is not None:
                            return pix
                    except Exception:
                        pass
            return None
        except Exception as e:
            logger.debug("Error in _get_item_pixbuf: %s", e)
            return None

    def _clear_button_children(self, button: Gtk.Button) -> None:
        try:
            for child in list(button.get_children()):
                try:
                    button.remove(child)
                except Exception:
                    try:
                        child.hide()
                    except Exception:
                        pass
        except Exception:
            pass

    def _refresh_item_ui(self, identifier: str, item: Any, button: Gtk.Button):
        pixbuf = self._get_item_pixbuf(item)
        self._clear_button_children(button)
        if pixbuf:
            img = Gtk.Image.new_from_pixbuf(pixbuf)
            try:
                button.set_image(img)
                button.set_always_show_image(True)
            except Exception:
                try:
                    button.add(img)
                    img.show()
                except Exception:
                    logger.debug("Could not put image into button")
        else:
            glyph = self._glyph_for_item(item)
            if glyph:
                lbl = Gtk.Label()
                try:
                    lbl.set_markup(f"<span font_desc='20'>{glyph}</span>")
                except Exception:
                    lbl.set_text(glyph)
                try:
                    button.add(lbl)
                    lbl.show()
                except Exception:
                    try:
                        placeholder = Gtk.Image.new_from_icon_name(
                            self.icon_resolver.default_icon, Gtk.IconSize.MENU
                        )
                        button.set_image(placeholder)
                        button.set_always_show_image(True)
                    except Exception:
                        pass
            else:
                try:
                    placeholder = Gtk.Image.new_from_icon_name(
                        self.icon_resolver.default_icon, Gtk.IconSize.MENU
                    )
                    button.set_image(placeholder)
                    button.set_always_show_image(True)
                except Exception:
                    pass
        tip = None
        try:
            tip = getattr(item, "tooltip", None)
            if callable(tip):
                try:
                    tip = tip()
                except Exception:
                    tip = None
            if tip is None:
                title = getattr(item, "title", None)
                if callable(title):
                    try:
                        title = title()
                    except Exception:
                        title = None
                tip = title
        except Exception:
            tip = None
        if tip:
            try:
                button.set_tooltip_text(str(tip))
            except Exception:
                pass
        else:
            try:
                button.set_has_tooltip(False)
            except Exception:
                pass
        try:
            button.show_all()
        except Exception:
            pass

    def _poll_tray(self) -> bool:
        try:
            if not self.tray:
                return True
            current_ids = set()
            try:
                items = getattr(self.tray, "items", None)
                if callable(items):
                    items = items()
                if items is None:
                    items = {}
                current_ids = set(items.keys())
            except Exception:
                current_ids = set()
            prev_ids = set(self.items_by_id.keys())
            for added in current_ids - prev_ids:
                try:
                    item_obj = items.get(added)
                    if item_obj is not None:
                        self.items_by_id[added] = item_obj
                        btn = self.do_bake_item_button(item_obj)
                        if btn:
                            self.buttons_by_id[added] = btn
                            self._add_button_to_layout(btn)
                            btn.show_all()
                except Exception as e:
                    logger.debug("Error adding tray item %s: %s", added, e)
            for removed in prev_ids - current_ids:
                try:
                    self.on_item_instance_removed(
                        removed, self.items_by_id.get(removed)
                    )
                except Exception:
                    pass
            self._update_visibility()
        except Exception as e:
            logger.debug("Poll tray error: %s", e)
        return True

    def on_item_instance_removed(self, identifier: str, removed_item: Any):
        if identifier is None:
            return
        if self.items_by_id.get(identifier) is removed_item:
            btn = self.buttons_by_id.pop(identifier, None)
            self.items_by_id.pop(identifier, None)
            if btn:
                try:
                    btn.destroy()
                except Exception:
                    pass
            if self.grid_enabled and self.grid_layout:
                for child in list(self.grid_layout.get_children()):
                    try:
                        self.grid_layout.remove(child)
                    except Exception:
                        pass
                for idx, btn in enumerate(self.buttons_by_id.values()):
                    row = idx // 5
                    col = idx % 5
                    try:
                        self.grid_layout.attach(btn, col, row, 1, 1)
                    except Exception:
                        pass
            self._update_visibility()

    def do_bake_item_button(self, item: Any) -> Optional[Gtk.Button]:
        icon_name = getattr(item, "icon_name", None)
        icon_pixmap = getattr(item, "icon_pixmap", None)
        title = getattr(item, "title", None)
        tooltip = getattr(item, "tooltip", None)
        if type(tooltip).__name__ == "SystemTrayItemToolTip":
            tooltip = None
        if not any([icon_name, icon_pixmap, title, tooltip]):
            return None
        btn = Button(name="statusbar-systray-item")
        setup_cursor_hover(btn, "pointer")
        btn.connect("button-press-event", lambda b, e: self.on_button_click(b, item, e))
        identifier = (
            getattr(item, "identifier", None)
            or getattr(item, "id", None)
            or getattr(item, "title", "unknown")
        )
        self._refresh_item_ui(str(identifier), item, btn)
        return btn

    def on_button_click(self, button: Gtk.Button, item: Any, event: Gdk.EventButton):
        if event.button == Gdk.BUTTON_PRIMARY:
            try:
                if hasattr(item, "activate"):
                    try:
                        item.activate(int(event.x_root), int(event.y_root))
                    except Exception as e:
                        s = str(e)
                        if "ServiceUnknown" in s or "not activatable" in s:
                            logger.debug("Activate suppressed (DBus): %s", s)
                        else:
                            logger.error("Activate error: %s", s)
                else:
                    logger.debug("Item has no activate()")
            except Exception as e:
                logger.debug("Unhandled activate error: %s", e)
        elif event.button == Gdk.BUTTON_SECONDARY:
            menu = None
            try:
                menu = getattr(item, "menu", None)
                if callable(menu):
                    try:
                        menu = menu()
                    except Exception:
                        menu = None
            except Exception:
                menu = None
            if isinstance(menu, Gtk.Menu):
                try:
                    menu.popup_at_widget(
                        button, Gdk.Gravity.SOUTH_WEST, Gdk.Gravity.NORTH_WEST, event
                    )
                except Exception as e:
                    logger.debug("popup_at_widget failed: %s", e)
            else:
                cm = getattr(item, "context_menu", None) or getattr(
                    item, "context_menu_for_event", None
                )
                if cm:
                    try:
                        try:
                            cm(int(event.x_root), int(event.y_root))
                        except TypeError:
                            try:
                                cm(event)
                            except Exception:
                                pass
                    except Exception as e:
                        logger.debug("ContextMenu error: %s", e)

    def _add_button_to_layout(self, btn: Gtk.Button):
        if self.grid_enabled and self.grid_layout:
            total = len(self.grid_layout.get_children())
            row = total // 4
            col = total % 4
            self.grid_layout.attach(btn, col, row, 1, 1)
        else:
            try:
                self.add(btn)
            except Exception:
                pass
