from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._core_config_handler import CoreConfigHandler


class LanguagePreviewCfg:
    def __init__(self, cfg: "CoreConfigHandler"):
        self._cfg = cfg
        self.parent = "language-preview"

    def enabled(self) -> bool:
        dflt = True
        i = self._cfg._get_nested(self.parent, "enabled", default=dflt)
        return i if isinstance(i, bool) else dflt

    def default_fullnames(self) -> dict:
        dflt = {
            "us": "English (US)",
            "en": "English",
            "ru": "Russian",
            "uk": "Ukrainian",
            "de": "German",
            "fr": "French",
            "es": "Spanish",
            "it": "Italian",
            "pt": "Portuguese",
            "cn": "Chinese",
            "jp": "Japanese",
        }
        i = self._cfg._get_nested(self.parent, "default-fullnames", default=dflt)
        return i if isinstance(i, dict) else dflt

    def margin(self) -> str:
        dflt = "0px 0px 0px 0px"
        return str(self._cfg._get_nested(self.parent, "margin", default=dflt))

    def layer(self) -> str:
        dflt = "top"
        return str(self._cfg._get_nested(self.parent, "layer", default=dflt))

    def position(self) -> str:
        dflt = "center"
        return str(self._cfg._get_nested(self.parent, "position", default=dflt))

    def replacer(self) -> dict:
        dflt = {
            "us": "en",
        }
        i = self._cfg._get_nested(self.parent, "replacer", default=dflt)
        return i if isinstance(i, dict) else dflt
