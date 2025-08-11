from ...modules.metrics.metrics import Metrics
from .._config_handler import ConfigHandler


def metrics_handler(cfg: ConfigHandler) -> Metrics:
    return Metrics(
        is_horizontal=cfg.bar.is_horizontal(),
        positions=cfg.metrics.positions(),
    )
