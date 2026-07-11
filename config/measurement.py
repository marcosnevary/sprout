from dataclasses import dataclass

MEASUREMENT_HEADER = (
    "timestamp",
    "sensor_1",
    "sensor_2",
)


@dataclass(frozen=True)
class MeasurementConfig:
    serial_port: str = "/dev/ttyACM0"
    command: str = "g"
    baud_rate: int = 115_200
    interval_between_measurements: int = 300
    max_measurements: int = 9_999_999
    measurements_filename: str = "measurements.csv"
    measurements_worksheet_name: str = "MEASUREMENTS"


MEASUREMENT_CONFIG = MeasurementConfig()
