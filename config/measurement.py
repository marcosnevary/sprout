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
    baud_rate: int = 115200
    interval_between_measurements: int = 300
    max_measurements: int = 9_999_999
    measurement_filename: str = "measurement.csv"
    measurement_worksheet_name: str = "Measurement"


MEASUREMENT_CONFIG = MeasurementConfig()
