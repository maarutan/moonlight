from ...modules.profile.profile import Profile
from .._config_handler import ConfigHandlerStatusBar


def profile_handler(cfg: ConfigHandlerStatusBar) -> Profile:
    return Profile(
        logo=cfg.profile.logo(),
        dashboard_profile_preview=cfg.profile.dashboard_profile_preview(),
    )
