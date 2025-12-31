# Single-Site Full Implementation
```mermaid
flowchart TD
GNSS["GNSS<br>(Reference Time Source)"] --> GM["PTP Grandmaster<br>(ptp4l)"]
GM --> BC["Boundary Clock Switch<br>(PTP-aware)"]
BC --> PTP["PTP Slave on RC<br>(ptp4l)"]
PTP --> PHC["NIC PHC<br>(Hardware Clock)"]
PHC --> PHC2SYS["phc2sys"]
PHC2SYS --> SYSCLK["System Clock<br>(CLOCK_REALTIME)"]
SYSCLK --> APP["Radar Application<br>(on RC)"]
```
Nodes:
- GNSS: provides the reference time source
- PTP Grandmaster (GM): site-local clock disciplined by GNSS
- Boundary Clock Switch (BC): PTP-aware switch that relays timing from GM
- ptp4l: PTP slave process on RC that disciplines the NIC PHC to the GM
- phc2sys: disciplines the system clock (CLOCK_REALTIME) from the NIC PHC

Functions
- Applications read system clock
- Radar App runs the ptp4l, PHC, phc2sys, and other apps.

# Single-Site Software Timestamping (this project)
```mermaid
flowchart TD
GM["PTP Grandmaster<br>(VM1)"] --> PTP["PTP Slave<br>(VM2)"]
```

## Multi-Site Full Implementation
- Site A (GNSS + GM + BC + Radar)
- Site B (GNSS + GM + BC + Radar)
- Site C (GNSS + GM + BC + Radar)

Each site runs an independent PTP domain.
Cross-site alignment is via GNSS, not PTP over WAN.