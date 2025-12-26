#!/usr/bin/env bash
set -euo pipefail

# Source PHC: /dev/ptp0 (your NIC PHC)
PHC="${1:-/dev/ptp0}"
LOGDIR="${2:-./logs}"
mkdir -p "$LOGDIR"

# -s selects source clock (PHC)
# -c selects destination clock (system CLOCK_REALTIME)
# -m prints messages
phc2sys -s "$PHC" -c CLOCK_REALTIME -m \
  2>&1 | tee -a "$LOGDIR/phc2sys_$(basename "$PHC").log"