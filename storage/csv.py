import csv
from pathlib import Path

from video.metadata import VideoMetadata


def ensure_directory(file_path: Path) -> None:
    file_path.mkdir(parents=True, exist_ok=True)


def ensure_csv_header(file_path: Path, header: tuple[str, ...]) -> None:
    if not file_path.exists():
        with file_path.open("w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(header)


def save_measurement_to_csv(
    timestamp: str,
    sensor_1: float,
    sensor_2: float,
    file_path: Path,
) -> None:
    with file_path.open("a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, sensor_1, sensor_2])


def save_metadata_to_csv(
    metadata: VideoMetadata,
    file_path: Path,
) -> None:
    with file_path.open("a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                metadata.timestamp,
                metadata.filename,
                metadata.duration_seconds,
                metadata.size_mb,
                metadata.width_px,
                metadata.height_px,
                metadata.fps,
            ]
        )


def initialize_csv(data_path: Path, filename: str, header: tuple[str, ...]) -> Path:
    file_path = data_path / filename

    ensure_directory(data_path)
    ensure_csv_header(file_path, header)

    return file_path
