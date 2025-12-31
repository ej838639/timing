"""Logging functionality for ptplab events."""

import json
from datetime import datetime, timezone

from .events import Event, Severity


class EventLogger:
    """Logs ptplab events to a file in JSON format."""

    def __init__(self, log_path: str) -> None:
        """
        Initialize the event logger.

        Args:
            log_path: Path to the log file where events will be written
        """
        self.log_path = log_path
        self._file = None

    def __enter__(self):
        """Context manager entry."""
        self._file = open(self.log_path, "a", encoding="utf-8")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._file:
            self._file.close()

    def log_event(self, event: Event) -> None:
        """
        Log an event to the file.

        Args:
            event: The Event to log
        """
        if self._file is None:
            raise RuntimeError("EventLogger must be used as a context manager")

        # Convert event to JSON
        event_dict = {
            "timestamp": datetime.fromtimestamp(
                event.t_utc, tz=timezone.utc
            ).isoformat(),
            "t_utc": event.t_utc,
            "severity": event.severity.name,
            "kind": event.kind,
            "message": event.message,
        }
        self._file.write(json.dumps(event_dict) + "\n")
        self._file.flush()

    @staticmethod
    def read_events(log_path: str) -> list[Event]:
        """
        Read all events from a log file.

        Args:
            log_path: Path to the log file

        Returns:
            List of Event objects
        """
        events: list[Event] = []
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        event = Event(
                            t_utc=data["t_utc"],
                            severity=Severity[data["severity"]],
                            kind=data["kind"],
                            message=data["message"],
                        )
                        events.append(event)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        # Skip malformed lines
                        continue
        except FileNotFoundError:
            pass
        return events
