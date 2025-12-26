import time
from typing import Optional

from .config import Thresholds
from .events import EventEngine, Severity
from .log_tail import follow
from .parse_ptp import parse_servo, parse_port_state
from .plot import Series, plot_offset


def run_monitor(
    *,
    log_path: str,
    warn_ms: float = 1.0,
    alarm_ms: float = 5.0,
    lost_sync_s: float = 3.0,
    plot_every_s: float = 10.0,
) -> None:
    """
    Run the PTP log monitoring loop.

    This function tails a ptp4l log file, extracts servo data,
    generates alerts, and optionally plots offset vs time.
    """
    thresholds = Thresholds(
        warn_ms=warn_ms,
        alarm_ms=alarm_ms,
        lost_sync_seconds=lost_sync_s,
    )

    engine = EventEngine(thresholds)
    series = Series()
    last_plot_t: Optional[float] = None

    with open(log_path, "r", encoding="utf-8", errors="replace") as fp:
        for line in follow(fp):
            now = time.monotonic()

            servo = parse_servo(line, now)
            if servo:
                series.add(servo)
                for event in engine.on_servo(servo):
                    _print_event(event.severity, event.kind, event.message)
            else:
                state = parse_port_state(line, now)
                if state:
                    _print_event(
                        Severity.INFO,
                        "port_state",
                        f"{state.from_state} -> {state.to_state} ({state.reason})",
                    )

            lost = engine.check_lost_sync(now)
            if lost:
                _print_event(lost.severity, lost.kind, lost.message)

            if plot_every_s > 0:
                if last_plot_t is None or (now - last_plot_t) >= plot_every_s:
                    last_plot_t = now
                    plot_offset(series)


def _print_event(sev: Severity, kind: str, msg: str) -> None:
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"{ts} [{sev.name}] {kind}: {msg}")
