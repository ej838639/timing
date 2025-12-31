# Overview
This file explains how to analyze the events log on the local computer.

# Plot the offset vs time
Transfer the event log back to the local computer to plot and analyze.
```sh
export PTPJSON="ptp_events_7.jsonl"
uv run ptpanalyze --log logs/$PTPJSON --title "PTP Offset Analysis" --block
```