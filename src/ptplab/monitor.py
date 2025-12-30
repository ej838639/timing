import time
from datetime import datetime, timezone
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
    from_start: bool = False,
) -> None:
    """
    Run the PTP log monitoring loop.

    This function tails a ptp4l log file, extracts servo data,
    generates alerts, and optionally plots offset vs time.

    Args:
        log_path: Path to the ptp4l log file
        warn_ms: Warning threshold in milliseconds
        alarm_ms: Alarm threshold in milliseconds
        lost_sync_s: Lost sync timeout in seconds
        plot_every_s: Plot interval in seconds (0 disables)
        from_start: If True, process entire log from beginning; if False, tail only new lines
    """
    thresholds = Thresholds(
        warn_ms=warn_ms,
        alarm_ms=alarm_ms,
        lost_sync_seconds=lost_sync_s,
    )

    engine = EventEngine(thresholds)
    series = Series()
    last_plot_t: Optional[float] = None

    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as fp:
            for line in follow(fp, from_start=from_start):
                now_utc = time.time()  # UTC timestamp (seconds since epoch)
                now_str = datetime.now(timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%S.%fZ"
                )  # Show current UTC time, Z indicates UTC

                servo = parse_servo(line, now_utc)
                if servo:
                    series.add(servo)
                    for event in engine.on_servo(servo):
                        _print_event(event.severity, event.kind, event.message, now_str)
                else:
                    state = parse_port_state(line, now_utc)
                    if state:
                        _print_event(
                            Severity.INFO,
                            "port_state",
                            f"{state.from_state} -> {state.to_state} ({state.reason})",
                            now_str,
                        )

                lost = engine.check_lost_sync(now_utc)
                if lost:
                    _print_event(lost.severity, lost.kind, lost.message, now_str)

                if plot_every_s > 0:
                    if last_plot_t is None or (now_utc - last_plot_t) >= plot_every_s:
                        last_plot_t = now_utc
                        plot_offset(series)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
    except FileNotFoundError:
        print(f"Error: Log file not found: {log_path}")
        raise


def _print_event(sev: Severity, kind: str, msg: str, ts: str) -> None:
    print(f"{ts} [{sev.name}] {kind}: {msg}")
