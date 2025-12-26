from dataclasses import dataclass, field
from typing import List

import matplotlib.pyplot as plt

from .config import ns_to_ms
from .parse_ptp import ServoSample

@dataclass
class Series:
    t: List[float] = field(default_factory=list)
    offset_ms: List[float] = field(default_factory=list)

    def add(self, s: ServoSample) -> None:
        self.t.append(s.t_monotonic)
        self.offset_ms.append(ns_to_ms(s.offset_ns))

def plot_offset(series: Series, title: str = "PTP offset vs time") -> None:
    if not series.t:
        print("No samples yet.")
        return

    t0 = series.t[0]
    x = [ti - t0 for ti in series.t]

    plt.figure()
    plt.plot(x, series.offset_ms)
    plt.xlabel("Time (s)")
    plt.ylabel("Offset (ms)")
    plt.title(title)
    plt.grid(True)
    plt.show()