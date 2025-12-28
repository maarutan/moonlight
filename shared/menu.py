from typing import Iterable, Optional, Literal, Union
from fabric.utils.helpers import Gtk, Gdk
from fabric.widgets.container import Container


MenuChild = Union[Gtk.Widget, Gtk.MenuItem]


class Menu(Gtk.Menu, Container):
    def __init__(
        self,
        children: MenuChild | Iterable[MenuChild] | None = None,
        name: Optional[str] = None,
        visible: bool = True,
        all_visible: bool = False,
        style: Optional[str] = None,
        style_classes: Iterable[str] | str | None = None,
        tooltip_text: Optional[str] = None,
        tooltip_markup: Optional[str] = None,
        h_align: Literal["fill", "start", "end", "center", "baseline"]
        | Gtk.Align
        | None = None,
        v_align: Literal["fill", "start", "end", "center", "baseline"]
        | Gtk.Align
        | None = None,
        h_expand: bool = False,
        v_expand: bool = False,
        size: Iterable[int] | int | None = None,
        **kwargs,
    ) -> None:
        Gtk.Menu.__init__(self)
        Container.__init__(
            self,
            children,
            name,
            visible,
            all_visible,
            style,
            style_classes,
            tooltip_text,
            tooltip_markup,
            h_align,
            v_align,
            h_expand,
            v_expand,
            size,
            **kwargs,
        )

    def append(self, child: MenuChild) -> None:
        if isinstance(child, Gtk.MenuItem):
            child.show_all()
            super().append(child)
        else:
            mi = Gtk.MenuItem()
            mi.add(child)
            mi.show_all()
            super().append(mi)

    def add(self, child: MenuChild) -> None:
        self.append(child)

    def prepend(self, child: MenuChild) -> None:
        if isinstance(child, Gtk.MenuItem):
            child.show_all()
            super().prepend(child)
        else:
            mi = Gtk.MenuItem()
            mi.add(child)
            mi.show_all()
            super().prepend(mi)

    def insert(self, child: MenuChild, position: int) -> None:
        if isinstance(child, Gtk.MenuItem):
            child.show_all()
            super().insert(child, position)
        else:
            mi = Gtk.MenuItem()
            mi.add(child)
            mi.show_all()
            super().insert(mi, position)

    def remove(self, child: MenuChild) -> None:
        try:
            super().remove(child)
        except TypeError:
            for mi in self.get_children():
                if isinstance(mi, Gtk.MenuItem):
                    for c in mi.get_children():
                        if c is child:
                            super().remove(mi)
                            return
            raise

    def set_style(self, css: str) -> None:
        try:
            from fabric.utils import compile_css

            css_text = compile_css(css)
        except Exception:
            css_text = css if "{" in css else f"* {{ {css} }}"
        provider = Gtk.CssProvider()
        provider.load_from_data(css_text.encode())
        try:
            screen = Gdk.Screen.get_default()
            Gtk.StyleContext.add_provider_for_screen(
                screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
            )
        except Exception:
            Gtk.StyleContext.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def popup(self, widget):
        if hasattr(self, "popup_at_widget"):
            try:
                self.popup_at_widget(widget, Gdk.Gravity.SOUTH, Gdk.Gravity.NORTH, None)
                return
            except Exception:
                pass
        try:
            self.popup(None, None, None, None, 0, Gtk.get_current_event_time())
        except Exception:
            try:
                self.popup(None, None, None, None, 0, GLib.get_current_time())
            except Exception:
                pass

    def close(self):
        self.destroy()
        self.hide()


def menu(*args, **kwargs) -> Menu:
    return Menu(*args, **kwargs)
