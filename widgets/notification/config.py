from utils.configuration_handler import ConfigurationHandler
from utils.constants import Const


class ConfigHandlerNotification(ConfigurationHandler):
    def __init__(self):
        super().__init__()

        self.config = self.get_option("widgets.notification")
