"""Command-line interface for ptpanalyze."""

import argparse

from .analyzer import read_event_log, filter_events_by_kind
from .plot import plot_offset


def main() -> int:
    """Main entry point for ptpanalyze CLI."""
    parser = argparse.ArgumentParser(
        description="Analyze and visualize PTP timing event logs from ptplab"
    )
    parser.add_argument("--log", required=True, help="Path to ptplab event log file")
    parser.add_argument(
        "--filter",
        help="Filter events by kind (e.g., 'offset_alarm', 'offset_warn')",
    )
    parser.add_argument(
        "--title",
        default="PTP Offset Analysis",
        help="Plot window title",
    )
    parser.add_argument(
        "--block",
        action="store_true",
        help="Block until plot window is closed",
    )
    parser.add_argument(
        "--backend",
        help="Override matplotlib backend (e.g., 'QtAgg', 'TkAgg')",
    )

    args = parser.parse_args()

    # Read event log and extract offset data
    series = read_event_log(args.log)

    if not series.t:
        print(f"No offset events found in {args.log}")
        return 1

    # Apply filter if requested
    if args.filter:
        filtered = filter_events_by_kind(args.log, args.filter)
        print(f"Found {len(filtered)} {args.filter} events")

    # Plot the data
    plot_offset(series, title=args.title, block=args.block, backend=args.backend)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
