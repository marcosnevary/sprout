import time


def current_timestamp() -> str:
    return time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())


def countdown(interval: int, message: str) -> None:
    for remaining in range(interval, 0, -1):
        hours, remainder = divmod(remaining, 3600)
        minutes, seconds = divmod(remainder, 60)

        print(
            f"\r{message}: {hours:02d}:{minutes:02d}:{seconds:02d}",
            end="",
            flush=True,
        )

        time.sleep(1)
