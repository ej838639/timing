from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from .config import Thresholds, ns_to_ms
from .parse_ptp import ServoSample


class Severity(Enum):
    INFO = auto()
    WARN = auto()
    ALARM = auto()


@dataclass(frozen=True)
class Event:
    t_utc: float
    severity: Severity
    kind: str
    message: str


class EventEngine:
    def __init__(self, th: Thresholds):
        self.th = th
        self._last_servo_t: Optional[float] = None
        self._lost_sync_active = False

    def on_servo(self, s: ServoSample) -> list[Event]:
        ev: list[Event] = []
        self._last_servo_t = s.t_utc
        self._lost_sync_active = False

        off_ms = abs(ns_to_ms(s.offset_ns))
        if off_ms >= self.th.alarm_ms:
            ev.append(
                Event(
                    s.t_utc,
                    Severity.ALARM,
                    "offset_alarm",
                    f"Offset {off_ms:.3f} ms >= {self.th.alarm_ms} ms",
                )
            )
        elif off_ms >= self.th.warn_ms:
            ev.append(
                Event(
                    s.t_utc,
                    Severity.WARN,
                    "offset_warn",
                    f"Offset {off_ms:.3f} ms >= {self.th.warn_ms} ms",
                )
            )

        # Simple heuristic: if servo state not in tighter states, note it
        if s.state not in ("s0", "s1"):
            ev.append(
                Event(s.t_utc, Severity.INFO, "servo_state", f"Servo state {s.state}")
            )
        return ev

    def check_lost_sync(self, now_t: float) -> Optional[Event]:
        if self._last_servo_t is None:
            return None
        dt = now_t - self._last_servo_t
        if dt >= self.th.lost_sync_seconds and not self._lost_sync_active:
            self._lost_sync_active = True
            return Event(
                now_t,
                Severity.ALARM,
                "lost_sync",
                f"No servo updates for {dt:.1f}s (>= {self.th.lost_sync_seconds}s)",
            )
        return None
