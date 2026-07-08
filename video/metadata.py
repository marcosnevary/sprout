import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta
from fractions import Fraction
from pathlib import Path


@dataclass(frozen=True)
class VideoMetadata:
    timestamp: str
    filename: str
    duration_seconds: float
    size_mb: float
    width_px: int
    height_px: int
    fps: float


def extract_video_metadata(video_path: Path) -> VideoMetadata:
    cmd = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        "-select_streams",
        "v:0",
        str(video_path),
    ]

    result = subprocess.run(  # noqa: S603
        cmd,
        capture_output=True,
        text=True,
        check=True,
    )

    data = json.loads(result.stdout)

    stream = data["streams"][0]
    tags = stream.get("tags", {}) or data["format"].get("tags", {})

    timestamp = (
        datetime.fromisoformat(tags["creation_time"]) - timedelta(hours=5)
    ).replace(tzinfo=None)

    return VideoMetadata(
        timestamp=timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        filename=video_path.name,
        duration_seconds=float(data["format"]["duration"]),
        size_mb=round(int(data["format"]["size"]) / 1_000_000, 2),
        width_px=stream["width"],
        height_px=stream["height"],
        fps=round(float(Fraction(stream["r_frame_rate"])), 2),
    )
