import os
import time
from typing import Iterator, TextIO


def follow(fp: TextIO, poll_s: float = 0.2, from_start: bool = False) -> Iterator[str]:
    """Yield new lines as the file grows (like tail -f).

    Args:
        fp: File pointer to read from
        poll_s: Polling interval in seconds
        from_start: If True, start from beginning of file; if False, start from end
    """
    if not from_start:
        fp.seek(0, os.SEEK_END)
    while True:
        line = fp.readline()
        if line:
            yield line.rstrip("\n")
        else:
            time.sleep(poll_s)
