import csv
import time
from pathlib import Path

import serial

BAUD_RATE = 115200
FILE_NAME = "soil_moisture_readings.csv"
DATA_PATH = Path("data") / FILE_NAME


def trigger_measurement(
    port: str = "COM6",
    trigger_char: str = "g",
) -> tuple[bool, str]:
    """Send a trigger to the Arduino and return the measurement result.

    Parameters
    ----------
    port : str, default="COM6"
        Serial port address (e.g., "COM6" or "/dev/ttyUSB0").
    trigger_char : str, default="g"
        Command sent to the Arduino.

    Returns
    -------
    tuple[bool, str]
        A tuple containing:
        - True and the measurement record on success.
        - False and an error message on failure.

    """
    try:
        with serial.Serial(port, BAUD_RATE, timeout=10) as arduino:
            time.sleep(2)
            arduino.write(trigger_char.encode("utf-8"))
            response = arduino.readline().decode("utf-8").strip()

            if response:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                sensor_1, sensor_2 = response.split(",")

                DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
                file_exists = DATA_PATH.exists()

                with DATA_PATH.open("a", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    if not file_exists:
                        writer.writerow(["timestamp", "sensor_1", "sensor_2"])
                    writer.writerow([timestamp, sensor_1, sensor_2])

                return True, f"{timestamp} - Sensor 1: {sensor_1}, Sensor 2: {sensor_2}"

            return False, "No response received from Arduino."

    except serial.SerialException:
        return False, f"Error: Could not access port {port}."

    except Exception as e:
        return False, f"Unexpected error: {e!s}"


if __name__ == "__main__":
    result, message = trigger_measurement(port="/dev/ttyACM0")

    print(message)
