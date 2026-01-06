from utils.configuration_handler import ConfigurationHandler
from utils.constants import Const


class ConfigHandlerActivateLinux(ConfigurationHandler):
    def __init__(self):
        super().__init__(Const.APP_CONFIG_FILE)
        self.config = self.get_option("widgets.activatelinux")
