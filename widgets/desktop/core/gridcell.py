from fabric.widgets.box import Box


class GridOverlay(Box):
    def __init__(self, grid):
        super().__init__()
        self.grid = grid

        # Размер overlay = вся область сетки
        total_w = grid.cols * grid.cell_w + (grid.cols - 1) * grid.gap
        total_h = grid.rows * grid.cell_h + (grid.rows - 1) * grid.gap
        self.set_size_request(total_w, total_h)

        self.connect("draw", self.on_draw)

    def on_draw(self, widget, cr):
        cr.set_source_rgba(1, 1, 1, 0.1)  # цвет линий (белый, прозрачный)
        for gy in range(self.grid.rows):
            for gx in range(self.grid.cols):
                x, y = self.grid.cell_to_px(gx, gy)
                w, h = self.grid.cell_w, self.grid.cell_h
                cr.rectangle(x, y, w, h)
                cr.stroke()
        return False
