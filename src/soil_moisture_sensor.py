import csv
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import gspread
import serial
from rich.console import Console
from rich.progress import Progress

from src.display import live

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
        progress: Progress,
        sheet: gspread.Spreadsheet,
    ) -> None:
        self.serial_port = serial_port
        self.trigger_character = trigger_character
        self.interval_between_measurements = interval_between_measurements
        self.measurement_count = 0

        self.progress = progress
        self.wait_task = self.progress.add_task("", total=0, visible=False)

        self.sheet = sheet

    def trigger_measurement(self) -> None:
        try:
            with serial.Serial(self.serial_port, BAUD_RATE, timeout=10) as arduino:
                time.sleep(2)

                arduino.write(self.trigger_character.encode("utf-8"))
                response = arduino.readline().decode("utf-8").strip()

                if response:
                    timestamp = datetime.now(
                        tz=ZoneInfo("America/Sao_Paulo"),
                    ).strftime("%Y-%m-%d %H:%M:%S")

                    sensor_1, sensor_2 = response.split(",")

                    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
                    file_exists = DATA_PATH.exists()

                    with DATA_PATH.open(
                        "a",
                        encoding="utf-8",
                        newline="",
                    ) as file:
                        writer = csv.writer(file)

                        if not file_exists:
                            writer.writerow(
                                [
                                    "timestamp",
                                    "sensor_1",
                                    "sensor_2",
                                ],
                            )

                        writer.writerow(
                            [
                                timestamp,
                                sensor_1,
                                sensor_2,
                            ],
                        )

                    try:
                        self.sheet.append_row(
                            [
                                timestamp,
                                sensor_1,
                                sensor_2,
                            ],
                        )
                    except Exception as e:
                        console.print(
                            f"[yellow]Failed to upload to Google Sheets: {e!s}[/yellow]",
                        )

                    live.console.print(
                        f"[bold green][{timestamp}] Measurement #{self.measurement_count + 1} recorded:[/bold green] "
                        f"Sensor 1: {sensor_1}, Sensor 2: {sensor_2}",
                    )

                    self.measurement_count += 1

                    return

                timestamp = datetime.now(
                    tz=ZoneInfo("America/Sao_Paulo"),
                ).strftime("%Y-%m-%d %H:%M:%S")

                console.print(
                    f"[bold red][{timestamp}] No response received from Arduino.[/bold red]",
                )

        except serial.SerialException:
            timestamp = datetime.now(
                tz=ZoneInfo("America/Sao_Paulo"),
            ).strftime("%Y-%m-%d %H:%M:%S")

            console.print(
                f"[bold red][{timestamp}] Could not access port {self.serial_port}.[/bold red]",
            )

        except Exception as e:
            timestamp = datetime.now(
                tz=ZoneInfo("America/Sao_Paulo"),
            ).strftime("%Y-%m-%d %H:%M:%S")

            console.print(
                f"[bold red][{timestamp}] Unexpected error: {e!s}[/bold red]",
            )

    def wait_until_next_measurement(self) -> None:
        timestamp = datetime.now(
            tz=ZoneInfo("America/Sao_Paulo"),
        ).strftime("%Y-%m-%d %H:%M:%S")

        self.progress.reset(
            self.wait_task,
            total=self.interval_between_measurements,
            visible=True,
            description=f"[bold yellow][{timestamp}] Waiting for next measurement[/bold yellow]",
        )

        for _ in range(self.interval_between_measurements):
            time.sleep(1)
            self.progress.update(self.wait_task, advance=1)

        self.progress.update(self.wait_task, visible=False)
