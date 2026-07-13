import time


def current_timestamp() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def countdown(interval: int, message: str) -> None:
    for remaining in range(interval, -1, -1):
        hours, remainder = divmod(remaining, 3600)
        minutes, seconds = divmod(remainder, 60)

        print(
            f"\r{message}: {hours:02d}:{minutes:02d}:{seconds:02d}",
            end="",
            flush=True,
        )

        if remaining > 0:
            time.sleep(1)
    print()
