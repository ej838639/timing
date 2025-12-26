#!/usr/bin/env bash
set -euo pipefail

IFACE="${1:-eth0}"

echo "== ethtool -T (timestamping capabilities) for $IFACE =="
ethtool -T "$IFACE" || true

echo
echo "== PTP devices present =="
ls -l /dev/ptp* 2>/dev/null || echo "No /dev/ptp* devices found (likely no PHC-capable NIC)."

echo
echo "== ptp4l version =="
ptp4l -v || true

echo
echo "Tip: If you later add a PTP-capable NIC, you should see /dev/ptp0 and ethtool will show HW timestamping."