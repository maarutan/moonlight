from ...modules.profile.profile import Profile
from .._config_handler import ConfigHandler


def profile_handler(cfg: ConfigHandler) -> Profile:
    return Profile(
        logo=cfg.profile.logo(),
        dashboard_profile_preview=cfg.profile.dashboard_profile_preview(),
    )
