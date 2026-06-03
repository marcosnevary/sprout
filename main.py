import os
import threading
import tomllib
from pathlib import Path

from dotenv import load_dotenv

from src.camera_recorder import CameraRecorder
from src.loops import soil_moisture_loop, video_loop


def main() -> None:
    load_dotenv()

    with Path.open("config.toml", "rb") as f:
        config = tomllib.load(f)

    remote_cli_path = os.getenv("REMOTE_CLI_PATH")
    ssh_password = os.getenv("CAMERA_SSH_PASSWORD")

    recording_duration = config["recording_duration"]
    interval_between_recordings = config["interval_between_recordings"]
    interval_between_measurements = config["interval_between_measurements"]
    max_recordings = config["max_recordings"]
    serial_port = config["serial_port"]

    print("―" * 100)
    print("Recording duration:", recording_duration, "seconds")
    print(
        "Interval between recordings:",
        interval_between_recordings // 60,
        "minutes",
    )
    print(
        "Interval between measurements:",
        interval_between_measurements // 60,
        "minutes",
    )
    print("Maximum number of recordings:", max_recordings)
    print("―" * 100)

    recorder = CameraRecorder(
        remote_cli_path=remote_cli_path,
        recording_duration=recording_duration,
        interval_between_recordings=interval_between_recordings,
        ssh_password=ssh_password,
    )

    try:
        recorder.start_process()
        recorder.setup_camera_connection()

        t1 = threading.Thread(
            target=soil_moisture_loop,
            args=(serial_port, interval_between_measurements),
            daemon=True,
        )
        t2 = threading.Thread(target=video_loop, args=(recorder, max_recordings))

        t1.start()
        t2.start()

        t2.join()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received.")
    finally:
        recorder.cleanup()


if __name__ == "__main__":
    main()
