import os
import time
from typing import Iterator, TextIO


def follow(fp: TextIO, poll_s: float = 0.2, from_start: bool = False) -> Iterator[str]:
    """Yield new lines as the file grows (like tail -f).

    Args:
        fp: File pointer to read from
        poll_s: Polling interval in seconds
        from_start: If True, start from beginning of file and exit after reading all lines;
                    if False, start from end and continue polling for new lines
    """
    if not from_start:
        fp.seek(0, os.SEEK_END)
    while True:
        line = fp.readline()
        if line:
            yield line.rstrip("\n")
        else:
            # If from_start mode, exit after reading all existing lines
            if from_start:
                break
            # Otherwise, continue polling for new lines
            time.sleep(poll_s)
