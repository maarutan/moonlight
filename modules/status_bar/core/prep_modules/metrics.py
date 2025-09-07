from ...modules.metrics.metrics import Metrics
from .._config_handler import ConfigHandlerStatusBar


def metrics_handler(cfg: ConfigHandlerStatusBar) -> Metrics:
    return Metrics(
        is_horizontal=cfg.bar.is_horizontal(),
        positions=cfg.metrics.positions(),
    )
