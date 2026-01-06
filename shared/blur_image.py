import gi
import io
import os
import subprocess
import shutil
from pathlib import Path
from typing import Optional

from PIL import Image, ImageFilter

from fabric.widgets.widget import Widget
from fabric.utils import Gtk, GdkPixbuf  # type: ignore


class BlurImage(Gtk.Image, Widget):  # type: ignore
    def __init__(
        self,
        image_file: str,
        blur_radius: int = 8,
        svg_scale: float = 3.0,
        svg_max_width: Optional[int] = None,
        svg_max_height: Optional[int] = None,
        **kwargs,
    ):
        Gtk.Image.__init__(self)
        Widget.__init__(self, **kwargs)
        self._blur_radius = blur_radius
        self._cached_w = 0
        self._cached_h = 0
        self._svg_scale = svg_scale
        self._svg_max_width = svg_max_width
        self._svg_max_height = svg_max_height
        self._source_path = Path(image_file)
        self._orig_pil = self._load_image_resolving_svg(self._source_path)
        self.connect("size-allocate", self._on_size_allocate)
        self._refresh_pixbuf()

    def _pil_to_pixbuf(self, pil_img: Image.Image) -> GdkPixbuf.Pixbuf:
        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")
        loader = GdkPixbuf.PixbufLoader.new_with_type("png")
        loader.write(buf.getvalue())
        loader.close()
        return loader.get_pixbuf()  # type: ignore

    def _render_blurred(self, w: int, h: int) -> GdkPixbuf.Pixbuf:
        w = max(1, w)
        h = max(1, h)
        img = self._orig_pil.resize((w, h), Image.LANCZOS).filter(  # type: ignore
            ImageFilter.GaussianBlur(self._blur_radius)
        )  # type: ignore
        return self._pil_to_pixbuf(img)

    def _current_alloc_size(self) -> tuple[int, int]:
        w = self.get_allocated_width()
        h = self.get_allocated_height()
        sf = 1
        win = self.get_window()  # type: ignore
        if win is not None:
            sf = getattr(win, "get_scale_factor", lambda: 1)()
        return max(1, w * sf), max(1, h * sf)

    def _refresh_pixbuf(self):
        w, h = self._current_alloc_size()
        if (
            w == self._cached_w
            and h == self._cached_h
            and self.get_pixbuf() is not None  # type: ignore
        ):
            return
        pb = self._render_blurred(w, h)
        self.set_from_pixbuf(pb)
        self._cached_w, self._cached_h = w, h

    def _on_size_allocate(self, *_):
        self._refresh_pixbuf()

    def set_blur_radius(self, radius: int):
        self._blur_radius = max(0, int(radius))
        self._cached_w = 0
        self._cached_h = 0
        self._refresh_pixbuf()

    def set_image(self, image_file: str):
        self._source_path = Path(image_file)
        self._orig_pil = self._load_image_resolving_svg(self._source_path)
        self._cached_w = 0
        self._cached_h = 0
        self._refresh_pixbuf()

    def _load_image_resolving_svg(self, path: Path) -> Image.Image:
        if path.suffix.lower() == ".svg":
            png_path = path.with_suffix("")  # drop .svg
            png_path = png_path.with_name(png_path.name + ".auto.png")
            self._ensure_svg_raster(path, png_path)
            return Image.open(png_path).convert("RGBA")
        return Image.open(path).convert("RGBA")

    def _ensure_svg_raster(self, svg_path: Path, png_path: Path):
        svg_mtime = svg_path.stat().st_mtime
        png_mtime = png_path.stat().st_mtime if png_path.exists() else -1
        if png_mtime >= svg_mtime and png_path.exists():
            return
        png_path.parent.mkdir(parents=True, exist_ok=True)
        if self._try_cairosvg(svg_path, png_path):
            return
        if self._try_rsvg_convert(svg_path, png_path):
            return
        if self._try_resvg(svg_path, png_path):
            return
        raise RuntimeError(
            "Не найден рендерер SVG. Установи python-cairosvg или librsvg (rsvg-convert) или resvg."
        )

    def _try_cairosvg(self, svg_path: Path, png_path: Path) -> bool:
        try:
            import cairosvg  # type: ignore
        except Exception:
            return False
        w = None
        h = None
        if self._svg_max_width:
            w = int(self._svg_max_width)
        if self._svg_max_height:
            h = int(self._svg_max_height)
        cairosvg.svg2png(
            url=str(svg_path),
            write_to=str(png_path),
            scale=self._svg_scale,
            output_width=w,
            output_height=h,
        )
        return True

    def _try_rsvg_convert(self, svg_path: Path, png_path: Path) -> bool:
        if shutil.which("rsvg-convert") is None:
            return False
        cmd = ["rsvg-convert", str(svg_path), "-o", str(png_path)]
        if self._svg_max_width:
            cmd += ["-w", str(int(self._svg_max_width * self._svg_scale))]
        if self._svg_max_height:
            cmd += ["-h", str(int(self._svg_max_height * self._svg_scale))]
        subprocess.run(cmd, check=True)
        return True

    def _try_resvg(self, svg_path: Path, png_path: Path) -> bool:
        if shutil.which("resvg") is None:
            return False
        args = ["resvg", str(svg_path), str(png_path)]
        if self._svg_max_width:
            args += ["--width", str(int(self._svg_max_width * self._svg_scale))]
        if self._svg_max_height:
            args += ["--height", str(int(self._svg_max_height * self._svg_scale))]
        subprocess.run(args, check=True)
        return True
