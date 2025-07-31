from ...modules.memory_ram import MemoryRAM
from .._config_handler import ConfigHandler


def memory_ram_handler(conf: ConfigHandler) -> MemoryRAM:
    return MemoryRAM(
        icon=conf.get_memory_icon(),
        orientation_pos=conf.is_horizontal(),
        interval=conf.get_memory_interval(),
        format=conf.get_memory_format(),
    )
