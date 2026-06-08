import os
import threading
import tomllib
from pathlib import Path

from dotenv import load_dotenv

from src.camera_recorder import CameraRecorder
from src.display import (
    live,
    recorder_progress,
    sensor_progress,
)
from src.google_sheets import get_sheet
from src.loops import soil_moisture_loop, video_loop
from src.soil_moisture_sensor import SoilMoistureSensor


def main() -> None:
    load_dotenv()

    with Path.open("config.toml", "rb") as f:
        config = tomllib.load(f)

    remote_cli_path = os.getenv("REMOTE_CLI_PATH")
    ssh_password = os.getenv("CAMERA_SSH_PASSWORD")

    recording_duration = config["recording_duration"]
    interval_between_recordings = config["interval_between_recordings"]
    max_recordings = config["max_recordings"]

    interval_between_measurements = config["interval_between_measurements"]
    trigger_character = config["trigger_character"]
    serial_port = config["serial_port"]

    credentials_file = os.getenv("GOOGLE_CREDENTIALS_FILE")
    sheet_name = os.getenv("GOOGLE_SHEET_NAME")

    sheet = get_sheet(credentials_file, sheet_name)

    print("―" * 100)
    print("Recording duration:", recording_duration, "seconds")
    print(
        "Interval between recordings:",
        interval_between_recordings // 60,
        "minutes",
    )
    print("Maximum number of recordings:", max_recordings)
    print(
        "Interval between measurements:",
        interval_between_measurements // 60,
        "minutes",
    )
    print("Maximum number of measurements:", config["max_measurements"])
    print("Serial port:", serial_port)
    print("Trigger character:", trigger_character)
    print("―" * 100)

    camera_recorder = CameraRecorder(
        remote_cli_path=remote_cli_path,
        recording_duration=recording_duration,
        interval_between_recordings=interval_between_recordings,
        ssh_password=ssh_password,
        progress=recorder_progress,
    )

    soil_moisture_sensor = SoilMoistureSensor(
        serial_port=serial_port,
        interval_between_measurements=interval_between_measurements,
        trigger_character=trigger_character,
        progress=sensor_progress,
        sheet=sheet,
    )

    try:
        camera_recorder.start_process()
        camera_recorder.setup_camera_connection()

        with live:
            t1 = threading.Thread(
                target=soil_moisture_loop,
                args=(soil_moisture_sensor, max_recordings),
                daemon=True,
            )
            t2 = threading.Thread(
                target=video_loop,
                args=(camera_recorder, max_recordings),
            )
            t1.start()
            t2.start()
            t2.join()

    except KeyboardInterrupt:
        print("\nKeyboard interrupt received.")
    finally:
        camera_recorder.cleanup()


if __name__ == "__main__":
    main()
