import time

import serial


class Sensor:
    def __init__(self, serial_port: str, command: str, baud_rate: int) -> None:
        self.serial_port = serial_port
        self.command = command
        self.baud_rate = baud_rate

    def open_connection(self) -> serial.Serial:
        return serial.Serial(self.serial_port, self.baud_rate, timeout=10)

    def read_measurement(self, arduino: serial.Serial) -> str:
        time.sleep(2)
        arduino.write(self.command.encode("utf-8"))
        return arduino.readline().decode().strip()

    def parse_measurement(self, raw_measurement: str) -> tuple[float, float]:
        sensor_1, sensor_2 = raw_measurement.split(",")
        return float(sensor_1), float(sensor_2)

    def measure(self) -> tuple[float, float] | None:
        try:
            with self.open_connection() as arduino:
                raw_measurement = self.read_measurement(arduino)
                sensor_1, sensor_2 = self.parse_measurement(raw_measurement)
                return sensor_1, sensor_2
        except Exception as e:
            print(f"Error occurred while measuring: {e}")
            return None
