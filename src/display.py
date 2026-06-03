from rich.console import Console, Group
from rich.live import Live
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
)

console = Console()

sensor_progress = Progress(
    SpinnerColumn(),
    TextColumn("{task.description}"),
    BarColumn(),
    TextColumn("{task.completed}/{task.total}s"),
    TimeRemainingColumn(),
)

recorder_progress = Progress(
    SpinnerColumn(),
    TextColumn("{task.description}"),
    BarColumn(),
    TextColumn("{task.completed}/{task.total}s"),
    TimeRemainingColumn(),
)

live = Live(
    Group(sensor_progress, recorder_progress),
    console=console,
    refresh_per_second=10,
)
