from utils.configuration_handler import ConfigurationHandler


class ConfigHandlerLanguagePreview(ConfigurationHandler):
    def __init__(self):
        super().__init__()
        self.config = self.get_option("widgets.languagepreview")
