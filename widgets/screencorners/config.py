from utils.configuration_handler import ConfigurationHandler


class ConfigHandlerScreenCorners(ConfigurationHandler):
    def __init__(self):
        super().__init__()
        self.config = self.get_option("widgets.screencorners")
        self.config_statusbar = self.get_option("widgets.statusbar")
