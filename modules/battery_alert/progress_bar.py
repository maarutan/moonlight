from fabric.widgets.circularprogressbar import CircularProgressBar
from fabric.widgets.label import Label
from services.battery import BatteryService


class BatteryAlerProgressBar:
    def __init__(
        self,
    ):
        self.battery = BatteryService()
        self.progress_bar = CircularProgressBar(
            name="charging-popup-progressbar",
            value=float(self.battery.get_property("Percentage") or 0.0),
            size=124,
            line_width=24,
            start_angle=0,
            end_angle=360,
            max_value=100.00,
            child=Label(name="charging-popup-progressbar-icon", label="󱐋"),
        )
