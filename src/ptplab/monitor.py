import os
import time
from datetime import datetime, timezone
from typing import Optional

from .config import Thresholds
from .event_logger import EventLogger
from .events import EventEngine, Severity
from .log_tail import follow
from .parse_ptp import parse_servo, parse_port_state


def run_monitor(
    *,
    log_path: str,
    event_log_path: Optional[str] = None,
    warn_ms: float = 1.0,
    alarm_ms: float = 5.0,
    lost_sync_s: float = 3.0,
    from_start: bool = False,
) -> None:
    """
    Run the PTP log monitoring loop.

    This function tails a ptp4l log file, extracts servo data,
    and generates alerts.

    Args:
        log_path: Path to the ptp4l log file
        event_log_path: Path to write ptplab events log file (optional)
        warn_ms: Warning threshold in milliseconds
        alarm_ms: Alarm threshold in milliseconds
        lost_sync_s: Lost sync timeout in seconds
        from_start: If True, process entire log from beginning; if False, tail only new lines
    """
    thresholds = Thresholds(
        warn_ms=warn_ms,
        alarm_ms=alarm_ms,
        lost_sync_seconds=lost_sync_s,
    )

    engine = EventEngine(thresholds)

    # Prepare event logger
    event_logger = None
    if event_log_path:
        os.makedirs(
            os.path.dirname(os.path.abspath(event_log_path)) or ".", exist_ok=True
        )
        event_logger = EventLogger(event_log_path)
        event_logger.__enter__()

    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as fp:
            for line in follow(fp, from_start=from_start):
                now_utc = time.time()  # UTC timestamp (seconds since epoch)
                now_str = datetime.now(timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%S.%fZ"
                )  # Show current UTC time, Z indicates UTC

                servo = parse_servo(line, now_utc)
                if servo:
                    for event in engine.on_servo(servo):
                        _print_event(event.severity, event.kind, event.message, now_str)
                        if event_logger:
                            event_logger.log_event(event)
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
                    if event_logger:
                        event_logger.log_event(lost)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
    except FileNotFoundError:
        print(f"Error: Log file not found: {log_path}")
        raise
    finally:
        if event_logger:
            event_logger.__exit__(None, None, None)


def _print_event(sev: Severity, kind: str, msg: str, ts: str) -> None:
    print(f"{ts} [{sev.name}] {kind}: {msg}")
