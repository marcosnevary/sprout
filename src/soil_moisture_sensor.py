import csv
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import serial
from rich.console import Console
from rich.live import Live
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
)

BAUD_RATE = 115200
FILE_NAME = "soil_moisture_measurements.csv"
DATA_PATH = Path("data") / FILE_NAME


console = Console()


class SoilMoistureSensor:
    def __init__(
        self,
        serial_port: str,
        interval_between_measurements: int,
        trigger_character: str,
    ) -> None:
        self.serial_port = serial_port
        self.trigger_character = trigger_character
        self.interval_between_measurements = interval_between_measurements
        self.measurement_count = 0

    def trigger_measurement(
        self,
    ) -> None:
        try:
            with serial.Serial(self.serial_port, BAUD_RATE, timeout=10) as arduino:
                time.sleep(2)
                arduino.write(self.trigger_character.encode("utf-8"))
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

                    console.print(
                        f"[bold green][{timestamp}] Measurement #{self.measurement_count + 1} recorded:[/bold green] Sensor 1: {sensor_1}, Sensor 2: {sensor_2}",
                    )

                    self.measurement_count += 1
                    return

                console.print(
                    f"[bold red][{datetime.now(tz=ZoneInfo('America/Sao_Paulo')).strftime('%Y-%m-%d %H:%M:%S')}] No response received from Arduino.[/bold red]",
                )

        except serial.SerialException:
            console.print(
                f"[bold red][{datetime.now(tz=ZoneInfo('America/Sao_Paulo')).strftime('%Y-%m-%d %H:%M:%S')}] Could not access port {self.serial_port}.[/bold red]",
            )

        except Exception as e:
            console.print(
                f"[bold red][{datetime.now(tz=ZoneInfo('America/Sao_Paulo')).strftime('%Y-%m-%d %H:%M:%S')}] Unexpected error: {e!s}[/bold red]",
            )

    def wait_until_next_measurement(self) -> None:
        wait_progress = Progress(
            SpinnerColumn(),
            TextColumn(
                f"[bold yellow][{datetime.now(tz=ZoneInfo('America/Sao_Paulo')).strftime('%Y-%m-%d %H:%M:%S')}] Waiting for next measurement[/bold yellow]",
            ),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}s"),
            TimeRemainingColumn(),
        )

        wait_task = wait_progress.add_task(
            "",
            total=self.interval_between_measurements,
        )

        with Live(wait_progress, refresh_per_second=10):
            for _ in range(self.interval_between_measurements):
                time.sleep(1)
                wait_progress.update(wait_task, advance=1)


if __name__ == "__main__":
    soil_moisture_sensor = SoilMoistureSensor(
        serial_port="/dev/ttyACM0",
        interval_between_measurements=300,
        trigger_character="g",
    )
    soil_moisture_sensor.trigger_measurement()
