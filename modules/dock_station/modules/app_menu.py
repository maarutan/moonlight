from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.box import Box
from fabric.widgets.grid import Grid
from fabric.utils import DesktopApp, get_desktop_applications


class AppMenu(Window):
    def __init__(self):
        super().__init__(
            name="dock-station-app-menu",
            anchor="bottom center",
            layer="top",
            exlusivity="auto",
        )
        apps = get_desktop_applications()
        main_box = Box(name="dock-station-app-menu-main-box", orientation="v")
        for app in apps:
            print(app.get_icon_pixbuf())
        grid_box = Grid(
            row_spacing=5,
            column_spacing=10,
            column_homogeneous=True,
            row_homogeneous=False,
        )

        # ------- after adding all widgets -------
        main_box.add(grid_box)
        self.add(main_box)


print(AppMenu())
