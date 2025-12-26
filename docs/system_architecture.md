# Single-Site (Baseline)

GNSS
  ↓
PTP Grandmaster (site-local)
  ↓
Boundary Clock Switch
  ↓
Radar Compute / Server
   - ptp4l (slave)
   - phc2sys (PHC → system clock)

## Multi-Site (Future)

Site A (GNSS + GM + BC + Radar)
Site B (GNSS + GM + BC + Radar)
Site C (GNSS + GM + BC + Radar)

Each site runs an independent PTP domain.
Cross-site alignment is via GNSS, not PTP over WAN.