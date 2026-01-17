from fabric.widgets.label import Label


class DesktopWidget(Label):
    def __init__(self, desktop, gx, gy, gw=1, gh=1):
        super().__init__(
            label="Widget", style="background: #222; border-radius: 8px; padding: 8px;"
        )
        self.desktop = desktop
        self.gx, self.gy = gx, gy
        self.gw, self.gh = gw, gh
        self.dragging = False

        # Размер и позиция
        x, y = desktop.grid.cell_to_px(gx, gy)
        w, h = desktop.grid.size_px(gw, gh)
        self.set_size_request(w, h)
        self._grid_x = x
        self._grid_y = y

        # События мыши
        self.connect("button-press-event", self.on_button_press)
        self.connect("motion-notify-event", self.on_motion_notify)
        self.connect("button-release-event", self.on_button_release)

    # Начало drag
    def on_button_press(self, widget, event):
        if self.desktop.edit_mode:
            self.dragging = True
            self.drag_offset_x = event.x
            self.drag_offset_y = event.y
        return True

    # Drag в процессе движения
    def on_motion_notify(self, widget, event):
        if self.dragging:
            new_x = int(event.x_root - self.drag_offset_x)
            new_y = int(event.y_root - self.drag_offset_y)

            # Ограничение по границам
            new_x = max(
                0,
                min(
                    new_x,
                    self.desktop.root.get_allocated_width()
                    - self.get_allocated_width(),
                ),
            )
            new_y = max(
                0,
                min(
                    new_y,
                    self.desktop.root.get_allocated_height()
                    - self.get_allocated_height(),
                ),
            )

            self.desktop.root.move(self, new_x, new_y)
        return True

    # Drop и snap к сетке
    def on_button_release(self, widget, event):
        if self.dragging:
            self.dragging = False
            gx, gy = self.desktop.grid.px_to_cell(
                self.get_allocation().x, self.get_allocation().y
            )
            self.gx, self.gy = gx, gy
            x, y = self.desktop.grid.cell_to_px(gx, gy)
            self.desktop.root.move(self, x, y)
        return True

    # Показать/скрыть обводку
    def show_border(self):
        self.set_style(
            "background: #222;"
            "border-radius: 8px;"
            "padding: 8px;"
            "border: 3px solid rgba(255,255,255,0.5);"
        )

    def hide_border(self):
        self.set_style(
            "background: #222; border-radius: 8px; padding: 8px; border: none;"
            "margin:0px;"
        )
