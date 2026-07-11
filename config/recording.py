from dataclasses import dataclass

RECORDING_HEADER = (
    "timestamp",
    "filename",
    "duration_seconds",
    "size_mb",
    "width_px",
    "height_px",
    "fps",
)


@dataclass(frozen=True)
class RecordingConfig:
    remote_cli_path: str = (
        "/home/lid/Documents/CrSDK_v2.00.00_20251030a_Linux64PC/build/RemoteCli"
    )
    videos_path: str = "/home/lid/videos-camera/Main/"
    ssh_password: str = "ycvJJdSF"  # noqa: S105
    recording_duration: int = 10
    interval_between_recordings: int = 1_800
    upload_duration: int = 10
    max_recordings: int = 9_999_999
    metadata_filename: str = "metadata.csv"
    metadata_worksheet_name: str = "METADATA"


RECORDING_CONFIG = RecordingConfig()
