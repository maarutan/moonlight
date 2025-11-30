from shared.input import Input
from shared.switch import Switch
from typing import TYPE_CHECKING
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from shared.combotext import ComboText
from fabric.widgets.eventbox import EventBox
from fabric.widgets.centerbox import CenterBox
from utils.json_type_schema import block_position

from shared.module_selector import ModuleSelector


if TYPE_CHECKING:
    from ..settings import StatusBarConfig


class BarConfig:
    def __init__(self, init_class: "StatusBarConfig"):
        self.cfg = init_class
        self.bn = self.cfg.bar_name

    def make_section(self, is_vertical: bool = False) -> Box:
        v_path = f"{self.bn}.if-vertical" if is_vertical else self.bn

        gen_option = self.cfg.bar_confh.get_option(v_path)
        if not isinstance(gen_option, dict):
            gen_option = {}

        children: list = []

        if is_vertical:
            children.append(
                Label(name="option-subtitle", label="⚙ Vertical Mode Settings")
            )

        if "enabled" in gen_option or not is_vertical:
            bar_enabled = bool(self.cfg.bar_confh.get_option(f"{v_path}.enabled"))
            switch = Switch(active=bar_enabled)
            switch.connect_changed(
                lambda state: self.cfg.bar_confh.set_option(
                    f"{v_path}.enabled", value=state
                )
            )
            children.append(
                CenterBox(
                    name="sm_section-config-box",
                    orientation="h",
                    spacing=16,
                    start_children=Label(name="option-title", label="Enabled       :"),
                    end_children=switch,
                )
            )

        # 3️⃣ Position
        if "position" in gen_option or not is_vertical:
            combo_position = ComboText(
                items=block_position,
                active=1,
                h_align="fill",
                h_expand=True,
            )
            bar_position = self.cfg.bar_confh.get_option(f"{v_path}.position")
            combo_position.value = bar_position
            combo_position.connect_changed(
                lambda text: self.cfg.bar_confh.set_option(f"{v_path}.position", text)
            )
            children.append(
                CenterBox(
                    name="sm_section-config-box",
                    orientation="h",
                    start_children=Label(name="option-title", label="Position      : "),
                    end_children=EventBox(child=combo_position),
                )
            )

        # 4️⃣ Layer
        if "layer" in gen_option or not is_vertical:
            combo_layer = ComboText(
                items=["top", "bottom"],
                active=1,
                h_align="fill",
                h_expand=True,
            )
            bar_layer = self.cfg.bar_confh.get_option(f"{v_path}.layer")
            combo_layer.value = bar_layer
            combo_layer.connect_changed(
                lambda text: self.cfg.bar_confh.set_option(f"{v_path}.layer", text)
            )
            children.append(
                CenterBox(
                    name="sm_section-config-box",
                    orientation="h",
                    start_children=Label(name="option-title", label="Layer         : "),
                    end_children=EventBox(child=combo_layer),
                )
            )

        # 5️⃣ Margin
        if "margin" in gen_option or not is_vertical:
            input_margin = Input(
                name="sm_section-config-input",
                label_text="",
                initial_value="0 0 0 0",
                trigger="change",
            )
            bar_margin = self.cfg.bar_confh.get_option(f"{v_path}.margin")
            input_margin.set_value(bar_margin)
            input_margin.set_on_change_callback(
                lambda value: self.cfg.bar_confh.set_option(f"{v_path}.margin", value)
            )
            children.append(
                CenterBox(
                    name="sm_section-config-box",
                    orientation="h",
                    start_children=Label(name="option-title", label="Margin        : "),
                    end_children=EventBox(child=input_margin),
                )
            )

        # 6️⃣ Transparent
        if "transparent" in gen_option or not is_vertical:
            bar_is_transparent = bool(
                self.cfg.bar_confh.get_option(f"{v_path}.transparent")
            )
            switch_transparent = Switch(active=bar_is_transparent)
            switch_transparent.connect_changed(
                lambda state: self.cfg.bar_confh.set_option(
                    f"{v_path}.transparent", value=state
                )
            )
            children.append(
                CenterBox(
                    name="sm_section-config-box",
                    orientation="h",
                    spacing=16,
                    start_children=Label(name="option-title", label="Transparent   :"),
                    end_children=switch_transparent,
                )
            )

        if "rounded" in gen_option or not is_vertical:
            bar_rounded = self.cfg.bar_confh.get_option(f"{v_path}.rounded")
            input_rounded = Input(
                name="sm_section-config-input-rounded",
                label_text="",
                initial_value=bar_rounded or "",
                trigger="change",
            )
            input_rounded.set_on_change_callback(
                lambda value: self.cfg.bar_confh.set_option(f"{v_path}.rounded", value)
            )
            children.append(
                CenterBox(
                    name="sm_section-config-box",
                    orientation="h",
                    start_children=Label(name="option-title", label="Rounded       : "),
                    end_children=EventBox(child=input_rounded),
                )
            )

        return Box(
            name="sm_section-config-container",
            orientation="v",
            h_align="fill",
            v_align="fill",
            h_expand=True,
            v_expand=True,
            children=children,
        )

    def make_widget_section(self):
        from ......status_bar.bar import StatusBar

        widgets_list = StatusBar._get_registry_widgets()
        if isinstance(widgets_list, dict):
            widgets = list(widgets_list.keys())
        else:
            widgets = list(widgets_list)

        layout = self.cfg.bar_confh.get_option(f"{self.bn}.widgets.layout") or {
            "start": [],
            "center": [],
            "end": [],
        }

        layout_box = Box(
            name="sm_section-config-box",
            orientation="v",
            h_align="fill",
            v_align="fill",
            h_expand=True,
            v_expand=True,
        )

        start_selector = ModuleSelector(
            available=widgets,
            modules=list(layout.get("start", [])),
            name="start",
        )
        start_selector.connect_changed(
            lambda mods: self.cfg.bar_confh.set_option(
                f"{self.bn}.widgets.layout.start", mods
            )
        )

        center_selector = ModuleSelector(
            available=widgets,
            modules=list(layout.get("center", [])),
            name="center",
        )
        center_selector.connect_changed(
            lambda mods: self.cfg.bar_confh.set_option(
                f"{self.bn}.widgets.layout.center", mods
            )
        )

        end_selector = ModuleSelector(
            available=widgets,
            modules=list(layout.get("end", [])),
            name="end",
        )
        end_selector.connect_changed(
            lambda mods: self.cfg.bar_confh.set_option(
                f"{self.bn}.widgets.layout.end", mods
            )
        )

        layout_box.add(start_selector)
        layout_box.add(center_selector)
        layout_box.add(end_selector)

        return layout_box
