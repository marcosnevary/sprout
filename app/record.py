from pathlib import Path

from config.app import DATA_PATH, SPREADSHEET_NAME
from config.recording import RECORDING_CONFIG, RECORDING_HEADER
from devices.camera import Camera
from storage.csv import initialize_csv, save_metadata_to_csv
from storage.google_sheets import initialize_worksheet, save_metadata_to_worksheet
from utils.time import countdown, current_timestamp
from video.files import get_latest_video_index, get_video_path
from video.metadata import extract_video_metadata


def main() -> None:
    camera = Camera(
        remote_cli_path=RECORDING_CONFIG.remote_cli_path,
        ssh_password=RECORDING_CONFIG.ssh_password,
        recording_duration=RECORDING_CONFIG.recording_duration,
        max_recordings=RECORDING_CONFIG.max_recordings,
        delay_between_commands=RECORDING_CONFIG.delay_between_commands,
    )

    camera.connect()

    file_path = initialize_csv(
        data_path=DATA_PATH,
        filename=RECORDING_CONFIG.metadata_filename,
        header=RECORDING_HEADER,
    )

    worksheet = initialize_worksheet(
        credentials_file="credentials.json",
        spreadsheet_name=SPREADSHEET_NAME,
        worksheet_name=RECORDING_CONFIG.metadata_worksheet_name,
        header=RECORDING_HEADER,
    )

    videos_path = Path(RECORDING_CONFIG.videos_path)

    for i in range(RECORDING_CONFIG.max_recordings):
        camera.record()

        countdown(RECORDING_CONFIG.upload_duration, "Time for upload to complete")

        # TODO: Improve the latest video logic
        latest_video_index = get_latest_video_index(videos_path)
        latest_video_path = get_video_path(
            videos_path,
            latest_video_index,
        )

        print(
            f"[{current_timestamp()}] Recording {i + 1} completed (C{latest_video_index}.MP4)."
        )

        if latest_video_path.exists():
            metadata = extract_video_metadata(latest_video_path)

            save_metadata_to_csv(metadata, file_path)
            print(
                f"[{current_timestamp()}] Metadata for C{latest_video_index}.MP4 saved to {file_path}."
            )

            if worksheet:
                save_metadata_to_worksheet(metadata, worksheet)

                print(
                    f"[{current_timestamp()}] Metadata for C{latest_video_index}.MP4 saved to Google Sheets."
                )
        else:
            print(
                f"[{current_timestamp()}] Error: Video file {latest_video_path} does not exist."
            )

        countdown(
            RECORDING_CONFIG.interval_between_recordings,
            "Time until next recording",
        )


if __name__ == "__main__":
    main()
