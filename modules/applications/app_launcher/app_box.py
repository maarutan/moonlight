from typing import Iterator, List, Optional
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.widgets.image import Image
from fabric.utils import (
    DesktopApp,
    get_desktop_applications,
    idle_add,
    remove_handler,
    GLib,
)

from utils.widget_utils import setup_cursor_hover
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .launcher import AppLauncher


class AppsBox(Box):
    def __init__(
        self,
        class_init: "AppLauncher",
        spacing: int = 6,
    ):
        super().__init__(
            name="al_apps-box",
            orientation="v",
            spacing=spacing,
        )
        self._arranger_handler: int = 0
        self._all_apps = get_desktop_applications()
        self.conf = class_init

        self._last_filtered: List[DesktopApp] = []

        # Новые поля для управления выбором
        self.items: List[Button] = []  # список добавленных кнопок-элементов
        self.selected_index: int = -1  # -1 = ничего не выбрано

    def arrange_viewport(self, query: str = "") -> bool:
        # Отменяем предыдущий обработчик, очищаем виджеты и список
        remove_handler(self._arranger_handler) if self._arranger_handler else None
        self.children = []
        self.items = []
        self.selected_index = -1

        filtered = [
            app
            for app in self._all_apps
            if query.casefold()
            in (
                (app.display_name or "")
                + (" " + (app.name or "") + " ")
                + (app.generic_name or "")
            ).casefold()
        ]

        self._last_filtered = filtered

        filtered_iter: Iterator[DesktopApp] = iter(filtered)
        should_resize = len(filtered) == len(self._all_apps)

        # Изменил добавляемую функцию: теперь _add_next_application принимает iterator и добавляет в self.items
        self._arranger_handler = idle_add(
            lambda *args: self._add_next_application(*args)
            or (self._resize_viewport() if should_resize else False),
            filtered_iter,
            pin=True,
        )
        return False

    def _add_next_application(self, apps_iter: Iterator[DesktopApp]) -> bool:
        app = next(apps_iter, None)
        if not app:
            return False

        # создаём кнопку и сразу сохраняем её в self.items
        btn = self._bake_application_slot(app, index=len(self.items))
        self.add(btn)
        self.items.append(btn)
        return True

    def _resize_viewport(self) -> bool:
        try:
            parent = self.get_parent()
            parent.set_min_content_width(self.get_allocation().width)  # type: ignore
        except:
            return False
        return False

    def _bake_application_slot(
        self,
        app: DesktopApp,
        index: Optional[int] = None,
        **kwargs,
    ) -> Button:
        """
        Создаёт кнопку для приложения. index — позиция в текущем списке (если известна),
        используется для обработки клика/выбора.
        """

        def _on_clicked(*_):
            # При клике отметим элемент выбранным (но не переключим фокус)
            if isinstance(index, int):
                # помечаем выбор без потери фокуса
                try:
                    self.select_index(index)
                except Exception:
                    pass
            app.launch()
            # закрыть лончер
            try:
                self.conf.tools.close()
            except Exception:
                pass

        btn = Button(
            name="al_app-slot",
            child=Box(
                orientation="h",
                spacing=12,
                children=[
                    Image(pixbuf=app.get_icon_pixbuf(), h_align="start", size=32),
                    Label(
                        label=app.display_name or "Unknown",
                        v_align="center",
                        h_align="center",
                    ),
                ],
            ),
            tooltip_text=app.description,
            on_clicked=_on_clicked,
            **kwargs,
        )

        # Ховер/курсор
        setup_cursor_hover(btn)

        # Сохраним индекс внутри виджета, чтобы можно было извлечь при необходимости
        try:
            setattr(btn, "_appsbox_index", index)
        except Exception:
            pass

        return btn

    # -------------------------
    # Методы управления выбором
    # -------------------------
    def _mark_selected(self, index: int):
        """Добавляет/убирает класс 'selected' у виджетов; при отсутствии API - пробует альтернативы."""
        for i, w in enumerate(self.items):
            try:
                if i == index:
                    w.add_style_class("selected")
                else:
                    w.remove_style_class("selected")
            except Exception:
                # fallback: поменяем имя для css или alpha
                try:
                    if i == index:
                        w.set_name("al_app-slot-selected")
                    else:
                        w.set_name("al_app-slot")
                except Exception:
                    # last resort: no-op
                    pass

    def select_index(self, index: int):
        """Выбрать конкретный индекс и прокрутить так, чтобы он был видим."""
        if not self.items:
            self.selected_index = -1
            return

        if index < 0:
            index = 0
        if index >= len(self.items):
            index = len(self.items) - 1

        self.selected_index = index
        self._mark_selected(index)
        # Отложим скролл, чтобы GTK успел разместить элементы
        try:
            idle_add(lambda: self.ensure_visible(index))
        except Exception:
            # fallback без idle_add
            try:
                self.ensure_visible(index)
            except Exception:
                pass

    def select_down(self):
        """Перейти вниз (следующий элемент)."""
        if not self.items:
            return
        if self.selected_index < 0:
            self.select_index(0)
        else:
            self.select_index(min(len(self.items) - 1, self.selected_index + 1))

    def select_up(self):
        """Перейти вверх (предыдущий элемент)."""
        if not self.items:
            return
        if self.selected_index < 0:
            self.select_index(0)
        else:
            self.select_index(max(0, self.selected_index - 1))

    def clear_selection(self):
        self.selected_index = -1
        for w in self.items:
            try:
                w.remove_style_class("selected")
            except Exception:
                try:
                    w.set_name("al_app-slot")
                except Exception:
                    pass

    def get_selected(self) -> Optional[Button]:
        if 0 <= self.selected_index < len(self.items):
            return self.items[self.selected_index]
        return None

    # -------------------------
    # Скролл: обеспечить видимость
    # -------------------------
    def ensure_visible(self, index: int):
        """
        Скроллит self.conf.app_window.scrolled так, чтобы элемент index оказался в видимой области.
        Ставит элемент приблизительно в центр видимой области.
        """
        if not (0 <= index < len(self.items)):
            return

        # получаем scrolled из app_window
        try:
            scrolled = self.conf.app_window.scrolled
        except Exception:
            return

        try:
            vadj = scrolled.get_vadjustment()
        except Exception:
            return

        item = self.items[index]

        # Попробуем получить координаты элемента относительно контейнера (self)
        try:
            alloc = item.get_allocation()
            item_y = alloc.y
            item_h = alloc.height
        except Exception:
            # fallback: попытаемся через translate_coordinates
            try:
                tx, ty = item.translate_coordinates(self, 0, 0)
                item_y = ty
                # попытка получить высоту
                if hasattr(item, "get_allocated_height"):
                    item_h = item.get_allocated_height()
                else:
                    item_h = (
                        item.get_allocation().height
                        if hasattr(item, "get_allocation")
                        else 0
                    )
            except Exception:
                return

        # параметры прокрутки
        try:
            page = vadj.get_page_size()
            lower = vadj.get_lower()
            upper = vadj.get_upper()
        except Exception:
            # Если API другой - попытаемся стандартные атрибуты
            try:
                page = vadj.page_size
                lower = vadj.lower
                upper = vadj.upper
            except Exception:
                return

        # целевая позиция — центрирование элемента
        target = item_y - (page - item_h) / 2.0

        # clamp
        min_val = lower
        max_val = max(lower, upper - page)
        if target < min_val:
            target = min_val
        if target > max_val:
            target = max_val

        # применим значение — в idle, чтобы не мешать текущему циклу layout
        try:
            vadj.set_value(target)
        except Exception:
            try:
                # fallback
                vadj.value = target
            except Exception:
                pass
