import logging
import subprocess
import threading
import time
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from rich.console import Console
from rich.progress import (
    Progress,
)

from src.display import live

console = Console()

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("camera_recorder")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(
    LOG_DIR / "commands.log",
    encoding="utf-8",
)

formatter = logging.Formatter(
    "%(asctime)s.%(msecs)03d | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.propagate = False


class CameraRecorder:
    def __init__(
        self,
        remote_cli_path: str,
        recording_duration: int,
        interval_between_recordings: int,
        ssh_password: str,
        progress: Progress,
    ) -> None:
        self.remote_cli_path = remote_cli_path
        self.ssh_password = ssh_password
        self.recording_duration = recording_duration
        self.interval_between_recordings = interval_between_recordings
        self.process = None
        self.recording_count = 0

        self.progress = progress
        self.wait_task = self.progress.add_task("", total=0, visible=False)
        self.record_task = self.progress.add_task("", total=0, visible=False)

    def _log_stdout(self) -> None:
        try:
            for line in self.process.stdout:
                logger.info("STDOUT %s", line.rstrip())
        except Exception as error:
            logger.exception("STDOUT_THREAD_ERROR: %s", error)  # noqa: TRY401

    def _log_stderr(self) -> None:
        try:
            for line in self.process.stderr:
                logger.info("STDERR %s", line.rstrip())
        except Exception as error:
            logger.exception("STDERR_THREAD_ERROR: %s", error)  # noqa: TRY401

    def _send_command(
        self,
        command: str,
        delay: float = 1.0,
    ) -> None:
        logger.info(
            "SEND %r delay=%.3f",
            command,
            delay,
        )

        start = time.monotonic()

        self.process.stdin.write(f"{command}\n")
        self.process.stdin.flush()

        flush_time = time.monotonic() - start

        logger.info(
            "FLUSH %r took %.3fs",
            command,
            flush_time,
        )

        time.sleep(delay)

    def start_process(self) -> None:
        print("Starting RemoteCli process...")

        logger.info("PROCESS_START")

        self.process = subprocess.Popen(  # noqa: S603
            [self.remote_cli_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        threading.Thread(
            target=self._log_stdout,
            daemon=True,
        ).start()

        threading.Thread(
            target=self._log_stderr,
            daemon=True,
        ).start()

        time.sleep(5)

        logger.info("PROCESS_STARTED")

        print("RemoteCli started successfully")

    def setup_camera_connection(self) -> None:
        print("Connecting to camera...")

        logger.info("CAMERA_CONNECTION_START")

        self._send_command("1")
        self._send_command("1")
        self._send_command("y")
        self._send_command(self.ssh_password)
        self._send_command("1")

        logger.info("CAMERA_CONNECTION_DONE")

        print("Camera connected successfully")
        print("―" * 100)

    def record_video(self) -> None:
        self.recording_count += 1

        logger.info(
            "RECORDING_START #%s duration=%ss",
            self.recording_count,
            self.recording_duration,
        )

        self._send_command("6", delay=0)  # Movie Rec Button
        self._send_command("y", delay=0)  # Confirm Movie Rec Button
        self._send_command("2", delay=0)  # Down

        timestamp = datetime.now(tz=ZoneInfo("America/Sao_Paulo")).strftime(
            "%Y-%m-%d %H:%M:%S",
        )
        self.progress.reset(
            self.record_task,
            total=self.recording_duration,
            visible=True,
            description=f"[bold cyan][{timestamp}] Recording #{self.recording_count}[/bold cyan]",
        )
        for _ in range(self.recording_duration):
            time.sleep(1)
            self.progress.update(self.record_task, advance=1)
        self.progress.update(self.record_task, visible=False)

        live.console.print(
            f"[bold green][{timestamp}] Recording #{self.recording_count} completed![/bold green]",
        )

        logger.info(
            "RECORDING_STOP #%s",
            self.recording_count,
        )

        self._send_command("6", delay=0)  # Movie Rec Button
        self._send_command("y", delay=0)  # Confirm Movie Rec Button
        self._send_command("1", delay=0)  # Up

    def wait_until_next_recording(self) -> None:
        timestamp = datetime.now(tz=ZoneInfo("America/Sao_Paulo")).strftime(
            "%Y-%m-%d %H:%M:%S",
        )
        self.progress.reset(
            self.wait_task,
            total=self.interval_between_recordings,
            visible=True,
            description=f"[bold yellow][{timestamp}] Waiting for next recording[/bold yellow]",
        )
        for _ in range(self.interval_between_recordings):
            time.sleep(1)
            self.progress.update(self.wait_task, advance=1)
        self.progress.update(self.wait_task, visible=False)

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
