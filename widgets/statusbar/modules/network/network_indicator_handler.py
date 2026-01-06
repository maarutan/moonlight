from typing import TYPE_CHECKING
from utils.colors_parse import colors
from loguru import logger
from .network_indicator import indicator

if TYPE_CHECKING:
    from .network_widget import NetworkWidget


class NetworkIndicatorHandler:
    def __init__(self, network_widget: "NetworkWidget"):
        self.confh = network_widget

    def icon_handler(self) -> str:
        network = self.confh.is_internet_connection
        ind = indicator(network)
        if self.confh.ethernet_enabled:
            svg_string = ind["ethernet"]["enable"]
        elif self.confh.wifi_enabled:
            signal = self.confh.wifi_signal
            if signal <= 20:
                svg_string = ind["wifi"]["enable"]["critical"]
            elif signal <= 40:
                svg_string = ind["wifi"]["enable"]["low"]
            elif signal <= 70:
                svg_string = ind["wifi"]["enable"]["medium"]
            else:
                svg_string = ind["wifi"]["enable"]["high"]
        else:
            if not self.confh.wifi_enabled:
                svg_string = ind["wifi"]["disable"]

            if not self.confh.ethernet_enabled:
                svg_string = ind["ethernet"]["disable"]
            else:
                svg_string = ind["offline"]

        return svg_string
