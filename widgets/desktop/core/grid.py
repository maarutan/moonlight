class GridConfig:
    def __init__(
        self,
        cols: int,
        rows: int,
        cell_w: int,
        cell_h: int,
        gap: int = 8,
        offset_x: int = 0,
        offset_y: int = 0,
    ):
        self.cols = cols
        self.rows = rows
        self.cell_w = cell_w
        self.cell_h = cell_h
        self.gap = gap
        self.offset_x = offset_x
        self.offset_y = offset_y

    # Перевод координат ячейки в пиксели
    def cell_to_px(self, gx: int, gy: int):
        x = self.offset_x + gx * (self.cell_w + self.gap)
        y = self.offset_y + gy * (self.cell_h + self.gap)
        return x, y

    # Размер виджета в пикселях по размеру в ячейках
    def size_px(self, gw: int, gh: int):
        w = gw * self.cell_w + (gw - 1) * self.gap
        h = gh * self.cell_h + (gh - 1) * self.gap
        return w, h

    # Привязка пиксельной позиции к сетке
    def px_to_cell(self, px, py):
        gx = round((px - self.offset_x) / (self.cell_w + self.gap))
        gy = round((py - self.offset_y) / (self.cell_h + self.gap))
        gx = max(0, min(self.cols - 1, gx))
        gy = max(0, min(self.rows - 1, gy))
        return gx, gy
