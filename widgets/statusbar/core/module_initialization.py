from ..modules.systemtray.systemtray import SystemTrayWidget
from ..modules.workspaces.workspaces import WorkspacesWidget
from ..modules.clock import ClockWidget
from ..modules.windowtitle import WindowTitleWidget
from ..modules.language import LanguageWidget
from ..modules.battery.battery import BatteryWidget
from ..modules.systemmonitor.sysmonitor import SystemMonitorWidget
from ..modules.network.network_widget import NetworkWidget
from ..modules.headphones.headphone_widget import HeadphoneWidget


MODULES: dict[str, type] = {
    "clock": ClockWidget,
    "workspaces": WorkspacesWidget,
    "systemtray": SystemTrayWidget,
    "windowtitle": WindowTitleWidget,
    "language": LanguageWidget,
    "battery": BatteryWidget,
    "systemmonitor": SystemMonitorWidget,
    "network": NetworkWidget,
    "headphones": HeadphoneWidget,
}
