import os
import time
from typing import Iterator, TextIO

def follow(fp: TextIO, poll_s: float = 0.2) -> Iterator[str]:
    """Yield new lines as the file grows (like tail -f)."""
    fp.seek(0, os.SEEK_END)
    while True:
        line = fp.readline()
        if line:
            yield line.rstrip("\n")
        else:
            time.sleep(poll_s)
            