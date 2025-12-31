"""Read and analyze ptplab event logs."""

from ptplab.event_logger import EventLogger

from .plot import Series


def read_event_log(log_path: str) -> Series:
    """
    Read a ptplab event log file and extract servo offset data.

    Args:
        log_path: Path to the ptplab event log file

    Returns:
        Series object containing offset vs time data
    """
    series = Series()
    events = EventLogger.read_events(log_path)

    for event in events:
        # Extract offset data from offset_warn and offset_alarm events
        if event.kind in ("offset_warn", "offset_alarm"):
            # Extract offset value from message like "Offset 0.123 ms >= ..."
            try:
                parts = event.message.split()
                if len(parts) >= 2 and parts[0] == "Offset":
                    offset_ms = float(parts[1])
                    series.add(event.t_utc, offset_ms)
            except (ValueError, IndexError):
                pass

    return series


def filter_events_by_kind(log_path: str, kind: str) -> list:
    """
    Filter events from a log file by kind.

    Args:
        log_path: Path to the ptplab event log file
        kind: Event kind to filter for (e.g., 'offset_alarm', 'offset_warn')

    Returns:
        List of matching events
    """
    events = EventLogger.read_events(log_path)
    return [e for e in events if e.kind == kind]
