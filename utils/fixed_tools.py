from fabric.utils import Gtk, GLib


class FixedTools:
    def __init__(self, fixed_container):
        self.container = fixed_container
        self.managed_widgets = {}
        self.pending_updates = set()
        self.container.connect("size-allocate", self._on_resize)

    def _parse_margin(self, margin):
        """
        Парсит margin в формат (top, right, bottom, left)
        Поддерживает:
        - int/float: применяется ко всем сторонам
        - str: "10", "10 20", "10 20 30 40"
        - tuple/list с 1 элементом: ко всем сторонам
        - tuple/list с 2 элементами: (vertical, horizontal)
        - tuple/list с 4 элементами: (top, right, bottom, left)
        """
        # Обработка строк типа "30 30 30 30"
        if isinstance(margin, str):
            parts = [int(x.strip()) for x in margin.split()]
            if len(parts) == 1:
                m = parts[0]
                return (m, m, m, m)
            elif len(parts) == 2:
                v, h = parts
                return (v, h, v, h)
            elif len(parts) == 4:
                return tuple(parts)
            else:
                return (0, 0, 0, 0)

        if isinstance(margin, (int, float)):
            return (margin, margin, margin, margin)

        if isinstance(margin, (tuple, list)):
            if len(margin) == 1:
                m = margin[0]
                return (m, m, m, m)
            elif len(margin) == 2:
                v, h = margin
                return (v, h, v, h)  # top, right, bottom, left
            elif len(margin) == 4:
                return tuple(margin)

        # По умолчанию
        return (0, 0, 0, 0)

    def add(self, widget, anchor="top-left", margin=0):
        """
        Добавить виджет с якорем и margin.

        margin может быть:
        - int: все стороны одинаково
        - (vertical, horizontal): отступы по вертикали и горизонтали
        - (top, right, bottom, left): каждая сторона отдельно
        """
        margin_tuple = self._parse_margin(margin)
        self.managed_widgets[widget] = {"anchor": anchor, "margin": margin_tuple}

        if widget.get_parent() is None:
            self.container.put(widget, 0, 0)
        widget.show_all()
        GLib.idle_add(self.update_position, widget)

    def update_position(self, widget, container_allocation=None):
        """Обновить позицию виджета"""
        data = self.managed_widgets.get(widget)
        if not data:
            return

        anchor = data["anchor"]
        m_top, m_right, m_bottom, m_left = data["margin"]

        # Размеры контейнера
        if container_allocation:
            cont_w = container_allocation.width
            cont_h = container_allocation.height
        else:
            cont_w = self.container.get_allocated_width()
            cont_h = self.container.get_allocated_height()

        # Размеры виджета
        min_size, nat_size = widget.get_preferred_size()
        w = nat_size.width or widget.get_allocated_width()
        h = nat_size.height or widget.get_allocated_height()

        # Если размер ещё неизвестен, отложим обновление
        if w <= 0 or h <= 0 or cont_w <= 0 or cont_h <= 0:
            if widget not in self.pending_updates:
                self.pending_updates.add(widget)
                GLib.idle_add(self.update_position, widget)
            return

        self.pending_updates.discard(widget)

        # Расчет позиции по якорю
        x, y = 0, 0

        if anchor == "center":
            x = max(0, (cont_w - w) // 2)
            y = max(0, (cont_h - h) // 2)
        else:
            # Вертикальная позиция
            if "top" in anchor:
                y = m_top
            elif "bottom" in anchor:
                y = max(0, cont_h - h - m_bottom)
            else:  # center vertical
                y = max(0, (cont_h - h) // 2)

            # Горизонтальная позиция
            if "left" in anchor:
                x = m_left
            elif "right" in anchor:
                x = max(0, cont_w - w - m_right)
            else:  # center horizontal
                x = max(0, (cont_w - w) // 2)

        self.container.move(widget, int(x), int(y))

    def _on_resize(self, container, allocation):
        """Обработчик изменения размера контейнера"""
        for widget in list(self.managed_widgets.keys()):
            self.update_position(widget, allocation)

    def child_margin(self, widget, margin):
        """
        Изменить margin уже добавленного виджета.

        margin может быть:
        - str: "30 30 30 30" или "20 15" или "10"
        - int: все стороны одинаково
        - tuple/list: (top, right, bottom, left)
        """
        if widget not in self.managed_widgets:
            return

        margin_tuple = self._parse_margin(margin)
        self.managed_widgets[widget]["margin"] = margin_tuple
        self.update_position(widget)

    def remove(self, widget):
        """Удалить виджет из управления"""
        if widget in self.managed_widgets:
            del self.managed_widgets[widget]
            self.container.remove(widget)
        self.pending_updates.discard(widget)


# Примеры использования:
if __name__ == "__main__":
    window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
    window.set_default_size(800, 600)
    window.connect("destroy", Gtk.main_quit)

    fixed = Gtk.Fixed()
    tools = FixedTools(fixed)

    # Все стороны одинаково: margin = 10
    btn1 = Gtk.Button(label="Все 10px")
    tools.add(btn1, anchor="top-left", margin=10)

    # Вертикаль и горизонталь: margin = (20, 15)
    btn2 = Gtk.Button(label="V:20 H:15")
    tools.add(btn2, anchor="bottom-right", margin=(20, 15))

    # Каждая сторона отдельно: (top, right, bottom, left)
    btn3 = Gtk.Button(label="T:5 R:10 B:15 L:20")
    tools.add(btn3, anchor="top-right", margin=(5, 10, 15, 20))

    # Center без margin
    btn4 = Gtk.Button(label="Center")
    tools.add(btn4, anchor="center", margin=0)

    # Изменение margin после добавления (строковый формат)
    tools.child_margin(btn1, margin="30 30 30 30")

    window.add(fixed)
    window.show_all()
    Gtk.main()
