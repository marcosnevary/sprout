import subprocess
import time


class Camera:
    def __init__(
        self,
        remote_cli_path: str,
        ssh_password: str,
        recording_duration: int,
        max_recordings: int,
        delay_between_commands: float,
    ) -> None:
        self.remote_cli_path = remote_cli_path
        self.ssh_password = ssh_password
        self.recording_duration = recording_duration
        self.max_recordings = max_recordings
        self.delay_between_commands = delay_between_commands

    def _start_remote_cli(self) -> None:
        self.remote_cli = subprocess.Popen(  # noqa: S603
            [self.remote_cli_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        time.sleep(5)

    def _send_command(self, command: str) -> None:
        self.remote_cli.stdin.write(f"{command}\n")
        self.remote_cli.stdin.flush()
        time.sleep(self.delay_between_commands)

    def _setup_camera_connection(self) -> None:
        self._send_command("1")
        self._send_command("1")
        self._send_command("y")
        self._send_command(self.ssh_password)
        self._send_command("1")

    def _start_recording(self) -> None:
        self._send_command("6")  # Movie Rec Button
        self._send_command("y")  # Confirm Movie Rec Button
        self._send_command("2")  # Down
        self._send_command("")

    def _stop_recording(self) -> None:
        self._send_command("6")  # Movie Rec Button
        self._send_command("y")  # Confirm Movie Rec Button
        self._send_command("1")  # Up
        self._send_command("")

    def connect(self) -> None:
        self._start_remote_cli()
        self._setup_camera_connection()

    def record(self) -> None:
        self._start_recording()
        time.sleep(self.recording_duration - 4 * self.delay_between_commands)
        self._stop_recording()

    def cleanup(self) -> None:
        self._send_command("q")
        self.remote_cli.terminate()
        self.remote_cli.wait()
