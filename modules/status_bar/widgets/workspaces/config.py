from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from .workspaces import Workspaces


@dataclass
class WorkspacePreviewSpec:
    enabled: bool
    size: int
    event: Literal["hover", "click"]
    event_click: Literal["left", "middle", "right"]
    missing_behavior: str


@dataclass
class WorkspaceMagicSpec:
    enabled: bool
    icon: str


@dataclass
class WorkspaceSpec:
    orientation: Literal["h", "v"]
    numbering_enabled: bool
    numbering: list[str]
    max_visible: int
    enable_factory: bool
    preview: WorkspacePreviewSpec
    magic: WorkspaceMagicSpec


class ConfigResolver:
    def __init__(self, cfg: "Workspaces", orientation: Literal["h", "v"]):
        self.cfg = cfg
        self.orientation = orientation

    def resolve(self) -> WorkspaceSpec:
        base = "status-bar.widgets.workspaces"
        get = self.cfg.get_option
        pv = get(f"{base}.workspace-preview", {}) or {}
        magic = get(f"{base}.magic-workspace", {}) or {}

        spec = WorkspaceSpec(
            orientation=self.orientation,  # type: ignore
            numbering_enabled=bool(get(f"{base}.numbering-enabled", False)),
            numbering=get(f"{base}.numbering", []) or [],
            max_visible=int(get(f"{base}.max-visible-workspaces", 10)),
            enable_factory=bool(get(f"{base}.enable-buttons-factory", True)),
            preview=WorkspacePreviewSpec(
                enabled=bool(pv.get("enabled", False)),
                size=int(pv.get("size", 300)),
                event=str(pv.get("event", "click")),  # type: ignore
                event_click=str(pv.get("event_click", "right")),  # type: ignore
                missing_behavior=str(pv.get("missing-behavior", "hide")),
            ),
            magic=WorkspaceMagicSpec(
                enabled=bool(magic.get("enabled", False)),
                icon=str(magic.get("icon", "✨")),
            ),
        )

        if self.orientation == "v":
            override = get(f"{base}.if-vertical", {}) or {}
            # apply override declaratively
            for field, value in override.items():
                if field == "workspace-preview":
                    spec.preview.__dict__.update(value)
                elif field == "magic-workspace":
                    spec.magic.__dict__.update(value)
                elif hasattr(spec, field.replace("-", "_")):
                    setattr(spec, field.replace("-", "_"), value)
        return spec
