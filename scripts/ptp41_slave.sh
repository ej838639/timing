#!/usr/bin/env bash
set -euo pipefail

IFACE="${1:-eth0}"
DOMAIN="${2:-0}"
LOGDIR="${3:-./logs}"
mkdir -p "$LOGDIR"

# -m prints to stdout; also tee to a file for parsing
# -S forces software timestamping (good for learning when no NIC HW TS)
# If you later have HW timestamping, switch -S -> -H (or omit, depending on NIC/driver)
ptp4l -i "$IFACE" -m -S -f /etc/linuxptp/ptp4l.conf -d "$DOMAIN" \
  2>&1 | tee -a "$LOGDIR/ptp4l_${IFACE}_d${DOMAIN}.log"