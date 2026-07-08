from pathlib import Path


def get_latest_video_index(videos_path: Path) -> int:
    video_files = list(videos_path.glob("C*.MP4"))
    last_video_file = max(video_files, key=lambda f: f.stat().st_mtime)
    return int(last_video_file.stem[1:])


def get_video_path(videos_path: Path, index: int) -> Path:
    return videos_path / f"C{index:04d}.MP4"
