from fabric.widgets.svg import Svg
from utils.colors_parse import colors


class WindowIndicator:
    @staticmethod
    def get_svg(
        count: int, spacing: int = 40, radius: int = 8, svg_size: int = 24
    ) -> Svg:
        color = colors.get("text", "#ffffff")

        if count <= 0:
            empty = f'<svg width="{svg_size}" height="{svg_size}" viewBox="0 0 {svg_size} {svg_size}" xmlns="http://www.w3.org/2000/svg"></svg>'
            return Svg(svg_string=empty, size=5)

        total_group_width = (spacing * (count - 1)) + 2 * radius
        svg_width = max(svg_size, int(total_group_width))
        svg_height = svg_size
        start_cx = (svg_width - total_group_width) / 2 + radius
        cy = svg_height / 2

        dots = []
        for i in range(count):
            cx = start_cx + i * spacing
            dots.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{color}"/>')

        icon = f"""
        <svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg">
            {"".join(dots)}
        </svg>
        """
        return Svg(svg_string=icon, size=5)
