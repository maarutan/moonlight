import re
from typing import Optional, Tuple
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.button import Button
from fabric.utils.helpers import exec_shell_command, GLib
from fabric.hyprland import Hyprland, HyprlandEvent
from utils.constants import Const
from utils.events import event_close_popup
from utils.widget_utils import setup_cursor_hover
from .core.items_side import ItemsSide
from .core.config_items_side import ItemsSideConfig
from .utils import Utils


class StartMenu(Window):
    def __init__(self):
        self.utils = Utils(self)
        super().__init__(
            title=f"{Const.APPLICATION_NAME}-start-menu",
            name="start-menu",
            h_align="fill",
            v_align="fill",
            layer="top",
            anchor=self.utils._anchor(),
            margin="100px",
            keyboard_mode="on-demand",
            style="""
                border-radius: 8px;
                background:none;
                padding: 40px;
                min-width: 300px;
                min-height: 500px;
            """,
        )

        self.is_hidden = True
        self.current_select = None

        self.children_box = Box(
            name="start-menu",
            orientation="v",
            h_align="fill",
            h_expand=True,
        )

        self.close_btn = Button(
            label="x",
            name="sm_close-button",
            h_align="end",
            on_clicked=lambda *_: self.utils.toggle("hide"),
        )

        self.title_box = CenterBox(
            name="sm_title-box",
            v_align="start",
            start_children=Label(
                name="sm_title-label", label=f"{Const.APPLICATION_NAME} - Settings ⚙️"
            ),
            end_children=self.close_btn,
        )
        setup_cursor_hover(self.close_btn)

        self.reload_btn = Button(
            label=f"󰑓 Reload - {Const.APPLICATION_NAME.title()}",
            name="sm_reload-button",
            h_align="end",
            on_clicked=self.reload_app,
        )

        self.close_btn_2 = Button(
            label="x",
            name="sm_close-button_2",
            h_align="end",
            on_clicked=lambda *_: self.utils.toggle("hide"),
        )
        setup_cursor_hover(self.close_btn_2)
        setup_cursor_hover(self.reload_btn)

        self.items_side = ItemsSide(self)
        self.items_side_config = ItemsSideConfig(self)
        self.selected_label = Label(label="")

        self.window_sides = CenterBox(
            name="sm_sides",
            h_align="center",
            v_align="center",
            start_children=self.items_side,
            center_children=Box(name="sm_center-line"),
            end_children=self.items_side_config,
        )

        self.children_box.add(self.title_box)
        self.children_box.add(self.window_sides)
        self.children_box.add(
            Box(
                h_align="end",
                orientation="h",
                children=[self.close_btn_2, self.reload_btn],
            )
        )

        self.add(self.children_box)

        self.hypr = Hyprland(commands_only=False)

        self.hypr.connect("event::changefloatingmode", self._on_hypr_event)
        event_close_popup(lambda: self.utils.toggle("hide"))

        self._refresh_layer()
        self.add_keybinding("Escape", lambda: self.utils.toggle("hide"))

    def _on_hypr_event(self, _svc: Hyprland, event: HyprlandEvent):
        self._refresh_layer()

    def _get_active_workspace_id(self) -> Optional[str]:
        reply = Hyprland.send_command("/activeworkspace")
        data = reply.reply.decode(errors="ignore")
        m = re.search(r"workspace\s+ID\s+([^\s\(\)]+)", data, re.IGNORECASE)
        if m:
            return m.group(1)
        m2 = re.search(r"\bID\s+([^\s\(\)]+)", data, re.IGNORECASE)
        if m2:
            return m2.group(1)
        return None

    def _analyze_workspace(self) -> Tuple[bool, bool]:
        ws_id = self._get_active_workspace_id()
        reply = Hyprland.send_command("/clients")
        txt = reply.reply.decode(errors="ignore").splitlines()

        has_any = False
        has_floating = False

        cur_block: dict[str, str] = {}

        def finalize_block():
            nonlocal has_any, has_floating, ws_id, cur_block
            if not cur_block:
                return
            w = cur_block.get("workspace")
            f = cur_block.get("floating")
            if ws_id is None or (w is not None and w == ws_id):
                has_any = True or has_any
                if f in ("yes", "true", "1"):
                    has_floating = True
            cur_block = {}

        for line in txt:
            line = line.strip()
            if not line:
                finalize_block()
                continue
            if line.startswith("Client"):
                finalize_block()
                continue
            if line.startswith("workspace:"):
                val = line.split(":", 1)[1].strip()
                val = val.split()[0]
                cur_block["workspace"] = val
            elif line.startswith("floating:"):
                val = line.split(":", 1)[1].strip().lower()
                cur_block["floating"] = val

        finalize_block()
        return has_any, has_floating

    def _refresh_layer(self):
        has_any, has_floating = self._analyze_workspace()
        if not has_any:
            self.layer = "top"
        else:
            if has_floating:
                self.layer = "bottom"
            else:
                self.layer = "top"

    def update_selection(self, name: str):
        self.current_select = name
        if hasattr(self, "items_side_config"):
            self.items_side_config.update_preview(name)

    def reload_app(self):
        self.utils.toggle("hide")
        GLib.timeout_add(
            200,
            lambda *_: exec_shell_command(
                f"bash -c 'kill -HUP $(cat {Const.APP_PID_FILE})'"
            ),
        )
