import os
import tomllib
from pathlib import Path

from dotenv import load_dotenv

from src.camera_recorder import CameraRecorder

# from src.soil_moisture_sensor import trigger_measurement


def main() -> None:
    load_dotenv()

    with Path.open("config.toml", "rb") as f:
        config = tomllib.load(f)

    remote_cli_path = os.getenv("REMOTE_CLI_PATH")
    ssh_password = os.getenv("CAMERA_SSH_PASSWORD")

    recording_duration = config["recording_duration"]
    interval_between_recordings = config["interval_between_recordings"]
    max_recordings = config["max_recordings"]
    # serial_port = config["serial_port"]

    print("―" * 100)
    print("Recording duration:", recording_duration, "seconds")
    print(
        "Interval between recordings:",
        interval_between_recordings // 60,
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

        for _ in range(max_recordings):
            # result, message = trigger_measurement(port=serial_port)
            # if result:
            #     print("Humidity reading acquired successfully:")
            #     print(message)
            # else:
            #     print("Failed to acquire humidity reading:")
            #     print(message)

            recorder.record_video()
            recorder.wait_until_next_recording()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received.")
    finally:
        recorder.cleanup()


if __name__ == "__main__":
    main()
