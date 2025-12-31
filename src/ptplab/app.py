import argparse
from ptplab.monitor import run_monitor


def main() -> int:
    parser = argparse.ArgumentParser(
        description="PTP log monitor and alerting application"
    )
    parser.add_argument("--log", required=True, help="Path to ptp4l log file")
    parser.add_argument(
        "--event-log",
        help="Path to write ptplab event log file (optional)",
    )
    parser.add_argument("--warn-ms", type=float, default=1.0)
    parser.add_argument("--alarm-ms", type=float, default=5.0)
    parser.add_argument("--lost-sync-s", type=float, default=3.0)
    parser.add_argument(
        "--from-start",
        action="store_true",
        help="Process entire log file from beginning instead of tailing only new lines",
    )

    args = parser.parse_args()

    run_monitor(
        log_path=args.log,
        event_log_path=args.event_log,
        warn_ms=args.warn_ms,
        alarm_ms=args.alarm_ms,
        lost_sync_s=args.lost_sync_s,
        from_start=args.from_start,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
