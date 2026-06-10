import json
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

from scripts.google_sheets import get_sheet
from src.display import live

load_dotenv()

PROCESSED_VIDEOS_FILE = Path(os.getenv("PROCESSED_VIDEOS_FILE"))


def load_processed_videos() -> set:
    if PROCESSED_VIDEOS_FILE.exists():
        return set(json.loads(PROCESSED_VIDEOS_FILE.read_text()))

    return set()


def save_processed_videos(processed_videos: set) -> None:
    PROCESSED_VIDEOS_FILE.parent.mkdir(parents=True, exist_ok=True)

    PROCESSED_VIDEOS_FILE.write_text(
        json.dumps(list(processed_videos), indent=2),
    )


def get_video_metadata(video_path: str) -> dict:
    video_path = Path(video_path)

    cmd = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(video_path),
    ]

    result = subprocess.run(  # noqa: S603
        cmd,
        capture_output=True,
        text=True,
        check=True,
    )

    data = json.loads(result.stdout)

    video_stream = next(s for s in data["streams"] if s["codec_type"] == "video")
    tags_video = video_stream.get("tags", {})
    tags_format = data["format"].get("tags", {})

    timestamp = tags_video.get("creation_time") or tags_format.get("creation_time")
    timestamp = datetime.fromisoformat(timestamp)
    timestamp = timestamp - timedelta(hours=5)
    timestamp = timestamp.replace(tzinfo=None)

    video_name = video_path.name
    video_duration_seconds = float(data["format"]["duration"])

    video_size_mb = round(int(data["format"]["size"]) / 1_000_000, 2)
    video_width_px = video_stream["width"]
    video_height_px = video_stream["height"]

    fps_str = video_stream.get("r_frame_rate", "0/1")
    num, den = map(int, fps_str.split("/"))
    fps = num / den if den else 0
    video_fps = round(fps, 2)

    return {
        "video_timestamp": timestamp,
        "video_name": video_name,
        "video_duration_seconds": video_duration_seconds,
        "video_size_mb": video_size_mb,
        "video_width_px": video_width_px,
        "video_height_px": video_height_px,
        "video_fps": video_fps,
    }


def upload_video_metadata_to_google_sheets() -> None:
    load_dotenv()

    videos_path = os.getenv("VIDEOS_PATH")
    credentials_file = os.getenv("GOOGLE_CREDENTIALS_FILE")
    spreadsheet_name = os.getenv("GOOGLE_SPREADSHEET_NAME")
    worksheet_name = os.getenv("VIDEO_METADATA_WORKSHEET_NAME")

    header = [
        "video_timestamp",
        "video_name",
        "video_duration_seconds",
        "video_size_mb",
        "video_width_px",
        "video_height_px",
        "video_fps",
    ]

    sheet = get_sheet(
        credentials_file=credentials_file,
        spreadsheet_name=spreadsheet_name,
        worksheet_name=worksheet_name,
        header=header,
    )

    processed = load_processed_videos()

    for video in Path(videos_path).glob("*.MP4"):
        if video.name in processed:
            continue

        info = get_video_metadata(video)

        sheet.append_row(
            [
                str(info["video_timestamp"]),
                info["video_name"],
                info["video_duration_seconds"],
                info["video_size_mb"],
                info["video_width_px"],
                info["video_height_px"],
                info["video_fps"],
            ],
        )

        processed.add(video.name)

        timestamp = datetime.now(tz=ZoneInfo("America/Sao_Paulo")).strftime(
            "%Y-%m-%d %H:%M:%S",
        )
        live.console.print(
            f"[bold green][{timestamp}] Metadata for {video} added.[/bold green]",
        )

    save_processed_videos(processed)
