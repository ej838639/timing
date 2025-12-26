from dataclasses import dataclass

@dataclass(frozen=True)
class Thresholds:
    warn_ms: float = 1.0
    alarm_ms: float = 5.0
    lost_sync_seconds: float = 3.0   # if we stop seeing sane servo lines for this long => lost sync

def ns_to_ms(ns: float) -> float:
    return ns / 1e6
