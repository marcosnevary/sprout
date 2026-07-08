import time

from config.app import DATA_PATH, SPREADSHEET_NAME
from config.recording import RECORDING_CONFIG, RECORDING_HEADER
from devices.camera import Camera
from storage.csv import initialize_csv, save_metadata_to_csv
from storage.google_sheets import initialize_worksheet, save_metadata_to_worksheet
from video.files import get_latest_video_index, get_video_path
from video.metadata import extract_video_metadata


def main() -> None:
    camera = Camera(
        remote_cli_path=RECORDING_CONFIG.remote_cli_path,
        ssh_password=RECORDING_CONFIG.ssh_password,
        recording_duration=RECORDING_CONFIG.recording_duration,
        interval_between_recordings=RECORDING_CONFIG.interval_between_recordings,
        max_recordings=RECORDING_CONFIG.max_recordings,
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

    latest_video_index = get_latest_video_index(RECORDING_CONFIG.videos_path)

    for _ in range(RECORDING_CONFIG.max_recordings):
        camera.record()

        time.sleep(RECORDING_CONFIG.upload_duration)

        latest_video_index += 1
        latest_video_path = get_video_path(
            RECORDING_CONFIG.videos_path,
            latest_video_index,
        )

        if latest_video_path.exists():
            metadata = extract_video_metadata(latest_video_path)

            save_metadata_to_csv(metadata, file_path)

            if worksheet:
                save_metadata_to_worksheet(metadata, worksheet)

        time.sleep(RECORDING_CONFIG.interval_between_recordings)


if __name__ == "__main__":
    main()
