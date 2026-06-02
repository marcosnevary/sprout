import subprocess
import time
from contextlib import suppress
from datetime import datetime
from zoneinfo import ZoneInfo

from rich.console import Console
from rich.live import Live
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
)

console = Console()


class CameraRecorder:
    def __init__(
        self,
        remote_cli_path: str,
        recording_duration: int,
        interval_between_recordings: int,
        ssh_password: str,
    ) -> None:
        self.remote_cli_path = remote_cli_path
        self.ssh_password = ssh_password
        self.recording_duration = recording_duration
        self.interval_between_recordings = interval_between_recordings
        self.process = None
        self.recording_count = 0

    def _send_command(
        self,
        command: str,
        delay: float = 1.0,
    ) -> None:
        self.process.stdin.write(f"{command}\n")
        self.process.stdin.flush()

        time.sleep(delay)

    def start_process(self) -> None:
        print("Starting RemoteCli process...")

        self.process = subprocess.Popen(  # noqa: S603
            [self.remote_cli_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        time.sleep(5)

        print("RemoteCli started successfully")

    def setup_camera_connection(self) -> None:
        print("Connecting to camera...")

        self._send_command("1")
        self._send_command("1")
        self._send_command("y")
        self._send_command(self.ssh_password)
        self._send_command("1")

        print("Camera connected successfully")
        print("―" * 100)

    def record_video(self) -> None:
        self.recording_count += 1

        self._send_command("6", delay=0)
        self._send_command("y", delay=0)

        self._send_command("2", delay=0)
        self._send_command("", delay=0)
        self._send_command("6", delay=0)
        self._send_command("y", delay=0)

        recording_progress = Progress(
            SpinnerColumn(),
            TextColumn(
                f"[bold cyan][{datetime.now(tz=ZoneInfo('America/Sao_Paulo')).strftime('%Y-%m-%d %H:%M:%S')}] Recording #{self.recording_count}[/bold cyan]",
            ),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}s"),
            TimeRemainingColumn(),
        )

        recording_task = recording_progress.add_task(
            "",
            total=self.recording_duration,
        )

        with Live(recording_progress, refresh_per_second=10):
            for _ in range(self.recording_duration):
                time.sleep(1)
                recording_progress.update(recording_task, advance=1)

        self._send_command("1", delay=0)
        self._send_command("", delay=0)

    def wait_until_next_recording(self) -> None:
        wait_progress = Progress(
            SpinnerColumn(),
            TextColumn(
                f"[bold yellow][{datetime.now(tz=ZoneInfo('America/Sao_Paulo')).strftime('%Y-%m-%d %H:%M:%S')}] Waiting for next recording[/bold yellow]",
            ),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}s"),
            TimeRemainingColumn(),
        )

        wait_task = wait_progress.add_task(
            "",
            total=self.interval_between_recordings,
        )

        with Live(wait_progress, refresh_per_second=10):
            for _ in range(self.interval_between_recordings):
                time.sleep(1)
                wait_progress.update(wait_task, advance=1)

        print("―" * 100)

    def cleanup(self) -> None:
        print("Cleaning up process...")

        if self.process is None:
            return

        try:
            if self.process.poll() is None:
                with suppress(BrokenPipeError):
                    self._send_command("q", delay=0)

                self.process.terminate()

                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()

            print("Process terminated successfully")

        except Exception as error:
            print(f"Cleanup error: {error}")
