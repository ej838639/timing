import platform
from dataclasses import dataclass, field
from typing import List, Optional

import matplotlib
import matplotlib.pyplot as plt

# Use QtAgg backend for interactive plots on macOS
matplotlib.use("QtAgg")

plt.ion()  # Enable interactive mode

_fig = None
_ax = None
_line = None


def set_backend(backend: str) -> None:
    """
    Override the matplotlib backend for plotting.

    Args:
        backend: Backend name (e.g., 'QtAgg'). Only QtAgg is supported on macOS.

    Note: This should be called before any plots are created.
    """
    matplotlib.use(backend)


@dataclass
class Series:
    t: List[float] = field(default_factory=list)
    offset_ms: List[float] = field(default_factory=list)

    def add(self, *args, **kwargs) -> None:
        """Add a data point to the series.

        Can be called with either:
        - ServoSample object (for backward compatibility with ptplab)
        - Two floats (t_utc, offset_ms)
        """
        if (
            len(args) == 1
            and hasattr(args[0], "t_utc")
            and hasattr(args[0], "offset_ns")
        ):
            # ServoSample object from ptplab
            s = args[0]
            # Import here to avoid circular dependency
            from ptplab.config import ns_to_ms

            self.t.append(s.t_utc)
            self.offset_ms.append(ns_to_ms(s.offset_ns))
        elif len(args) == 2:
            # Direct values (t_utc, offset_ms)
            self.t.append(args[0])
            self.offset_ms.append(args[1])
        else:
            raise ValueError(
                "add() requires either a ServoSample or (t_utc, offset_ms)"
            )


def _raise_window(manager) -> None:
    """Try to bring the window to the foreground (best-effort)."""
    try:
        if hasattr(manager, "window"):
            window = manager.window
            if hasattr(window, "activateWindow"):
                window.activateWindow()
            if hasattr(window, "raise_"):
                window.raise_()
    except Exception:
        pass


def plot_offset(
    series: Series,
    title: str = "PTP offset vs time",
    block: bool = False,
    backend: Optional[str] = None,
) -> None:
    """
    Plot PTP offset vs time.

    Args:
        series: Data series to plot
        title: Plot window title
        block: If True, block until window is closed
        backend: Override matplotlib backend (e.g., 'QtAgg'). If None, uses QtAgg for macOS.
    """
    if backend:
        set_backend(backend)

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
        if hasattr(_fig.canvas, "manager") and _fig.canvas.manager is not None:
            if hasattr(_fig.canvas.manager, "set_window_title"):
                _fig.canvas.manager.set_window_title(title)
    else:
        _line.set_data(x, series.offset_ms)
        _ax.relim()
        _ax.autoscale_view()
        if hasattr(_fig.canvas, "manager") and _fig.canvas.manager is not None:
            if hasattr(_fig.canvas.manager, "set_window_title"):
                _fig.canvas.manager.set_window_title(title)

    _ax.set_title(title)
    _fig.canvas.draw_idle()
    _fig.canvas.flush_events()
    if _fig.canvas.manager is not None:
        _raise_window(_fig.canvas.manager)

    if block:
        # Keep window open until user closes it
        print("Plot displayed. Close the plot window to exit.")
        plt.ioff()  # Turn off interactive mode
        plt.show(block=True)  # Block until window is closed
    else:
        plt.pause(0.001)  # Allow the GUI to process events
        print("Plot displayed.")
