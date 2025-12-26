# Single-Site (Baseline)
```mermaid
flowchart TD
GNSS["GNSS<br>(Reference Time Source)"] --> GM["PTP Grandmaster<br>(Site-local)"]
GM --> BC["Boundary Clock Switch<br>(PTP-aware)"]
BC --> RC["Radar Compute / Server"]
RC --> PTP["ptp4l<br>(PTP Slave)"]
RC --> PHC["phc2sys<br>(PHC → System Clock)"]
PTP -.-> PHC
```

## Multi-Site (Future)
- Site A (GNSS + GM + BC + Radar)
- Site B (GNSS + GM + BC + Radar)
- Site C (GNSS + GM + BC + Radar)

Each site runs an independent PTP domain.
Cross-site alignment is via GNSS, not PTP over WAN.