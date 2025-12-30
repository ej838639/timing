from dataclasses import dataclass, field
from typing import List

import matplotlib

matplotlib.use("QtAgg")  # Qt backend for interactive plots on macOS
import matplotlib.pyplot as plt

plt.ion()  # Enable interactive mode

from .config import ns_to_ms
from .parse_ptp import ServoSample

_fig = None
_ax = None
_line = None


@dataclass
class Series:
    t: List[float] = field(default_factory=list)
    offset_ms: List[float] = field(default_factory=list)

    def add(self, s: ServoSample) -> None:
        self.t.append(s.t_utc)
        self.offset_ms.append(ns_to_ms(s.offset_ns))


def _raise_window(manager: matplotlib.backend_bases.FigureManagerBase) -> None:
    """Try to bring the window to the foreground (best-effort)."""
    try:
        window = manager.window
        window.activateWindow()
        window.raise_()
    except Exception:
        pass


def plot_offset(
    series: Series, title: str = "PTP offset vs time", block: bool = False
) -> None:
    if not series.t:
        print("No samples yet.")
        return

    global _fig, _ax, _line

    print(f"Plotting {len(series.t)} samples...")
    t0 = series.t[0]
    x = [ti - t0 for ti in series.t]

    if _fig is None:
        _fig, _ax = plt.subplots()
        (_line,) = _ax.plot(x, series.offset_ms, lw=1.5)
        _ax.set_xlabel("Time (s)")
        _ax.set_ylabel("Offset (ms)")
        _ax.grid(True)
        _fig.canvas.manager.set_window_title(title)
    else:
        _line.set_data(x, series.offset_ms)
        _ax.relim()
        _ax.autoscale_view()
        _fig.canvas.manager.set_window_title(title)

    _ax.set_title(title)
    _fig.canvas.draw_idle()
    _fig.canvas.flush_events()
    _raise_window(_fig.canvas.manager)

    if block:
        # Keep window open until user closes it
        print("Plot displayed. Close the plot window to exit.")
        plt.ioff()  # Turn off interactive mode
        plt.show(block=True)  # Block until window is closed
    else:
        plt.pause(0.001)  # Allow the GUI to process events
        print("Plot displayed.")
