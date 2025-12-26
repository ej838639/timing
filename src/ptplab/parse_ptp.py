import re
from dataclasses import dataclass
from typing import Optional

# Typical linuxptp ptp4l servo line patterns you often see:
# "... offset   -1234 s2 freq  +12 path delay  456"
# units vary by build/config; offset frequently in ns (but can be "s2" etc in message)
SERVO_RE = re.compile(
    r"offset\s+(?P<offset>-?\d+)\s+"
    r"(?P<state>s\d)\s+freq\s+(?P<freq>[+-]?\d+)\s+path\s+delay\s+(?P<delay>-?\d+)"
)

# State transitions / port state lines can look like:
# "port 1: LISTENING to UNCALIBRATED on INIT_COMPLETE"
# "port 1: UNCALIBRATED to SLAVE on MASTER_CLOCK_SELECTED"
PORT_STATE_RE = re.compile(r"port\s+\d+:\s+(?P<from>\w+)\s+to\s+(?P<to>\w+)\s+on\s+(?P<reason>.+)$")

@dataclass(frozen=True)
class ServoSample:
    t_monotonic: float
    offset_ns: int
    freq_ppb: int
    delay_ns: int
    state: str

@dataclass(frozen=True)
class PortStateChange:
    t_monotonic: float
    from_state: str
    to_state: str
    reason: str

def parse_servo(line: str, t_monotonic: float) -> Optional[ServoSample]:
    m = SERVO_RE.search(line)
    if not m:
        return None
    return ServoSample(
        t_monotonic=t_monotonic,
        offset_ns=int(m.group("offset")),
        freq_ppb=int(m.group("freq")),
        delay_ns=int(m.group("delay")),
        state=m.group("state"),
    )

def parse_port_state(line: str, t_monotonic: float) -> Optional[PortStateChange]:
    m = PORT_STATE_RE.search(line)
    if not m:
        return None
    return PortStateChange(
        t_monotonic=t_monotonic,
        from_state=m.group("from"),
        to_state=m.group("to"),
        reason=m.group("reason").strip(),
    )
