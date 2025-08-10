from ...modules.metrics import Metrics
from .._config_handler import ConfigHandler


def metrics_handler(cfg: ConfigHandler) -> Metrics:
    return Metrics(cfg.bar.is_horizontal())
