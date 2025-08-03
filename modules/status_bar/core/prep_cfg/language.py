from typing import Literal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._config_handler import ConfigHandler


class LanguageCfg:
    def __init__(self, cfg_handler: "ConfigHandler") -> None:
        self._cfg = cfg_handler
        self.parent = "language"

    def number_letters(self) -> int:
        dflt = 2
        i = self._cfg._get_nested(self.parent, "number_letters", default=dflt)
        return i if isinstance(i, int) else dflt

    def register(self) -> Literal["upper", "u", "lower", "l"]:
        dflt: Literal["lower"] = "lower"
        i = self._cfg._get_nested(self.parent, "register", default=dflt)

        if isinstance(i, str) and i in {"upper", "u", "lower", "l"}:
            return i  # type: ignore
        return dflt
