from ....cavalade.cavalade import SpectrumRender
from config.data import CAVA_APP_DIR
from .._config_handler import ConfigHandlerStatusBar
from fabric.widgets.stack import Stack


def cavalcade_handler(cfg: ConfigHandlerStatusBar) -> Stack:
    name = "statusbar_cavalcade.json"
    cavalcade = SpectrumRender(
        name=name,
        is_horizontal=cfg.bar.is_horizontal(),
        config_dir=CAVA_APP_DIR,
        config_file=CAVA_APP_DIR / name,
        width=180,
        height=40,
    )
    return Stack(children=cavalcade.get_spectrum_box())
