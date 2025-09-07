from ...modules.memory_ram import MemoryRAM
from .._config_handler import ConfigHandlerStatusBar


def memory_ram_handler(cfg: ConfigHandlerStatusBar) -> MemoryRAM:
    return MemoryRAM(
        icon=cfg.memory_ram.icon(),
        is_horizontal=cfg.bar.is_horizontal(),
        interval=cfg.memory_ram.interval(),
        format=cfg.memory_ram.format(),
    )
