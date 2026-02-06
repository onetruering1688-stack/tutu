#!/usr/bin/env python3
"""A simple time calculation CLI tool.

Examples:
  python time_tool.py duration --start "2024-01-01 10:00:00" --end "2024-01-01 12:30:00"
  python time_tool.py add --start "2024-01-01 10:00:00" --hours 1 --minutes 15
  python time_tool.py subtract --start "2024-01-01 10:00:00" --minutes 45
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable

DEFAULT_FORMAT = "%Y-%m-%d %H:%M:%S"


@dataclass(frozen=True)
class DurationResult:
    delta: timedelta

    def to_human(self) -> str:
        total_seconds = int(self.delta.total_seconds())
        sign = "-" if total_seconds < 0 else ""
        total_seconds = abs(total_seconds)
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        parts = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        if seconds or not parts:
            parts.append(f"{seconds}s")
        return sign + " ".join(parts)

    def to_hms(self) -> str:
        total_seconds = int(self.delta.total_seconds())
        sign = "-" if total_seconds < 0 else ""
        total_seconds = abs(total_seconds)
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{sign}{hours:02d}:{minutes:02d}:{seconds:02d}"


@dataclass(frozen=True)
class ParsedTime:
    value: datetime

    @classmethod
    def parse(cls, raw: str, fmt: str) -> "ParsedTime":
        return cls(datetime.strptime(raw, fmt))


@dataclass(frozen=True)
class TimeAdjustment:
    hours: int = 0
    minutes: int = 0
    seconds: int = 0

    def to_timedelta(self) -> timedelta:
        return timedelta(hours=self.hours, minutes=self.minutes, seconds=self.seconds)


def parse_time(raw: str, fmt: str) -> ParsedTime:
    return ParsedTime.parse(raw, fmt)


def ensure_any_adjustment(adjustment: TimeAdjustment) -> None:
    if adjustment.hours == 0 and adjustment.minutes == 0 and adjustment.seconds == 0:
        raise SystemExit("Please provide at least one of --hours/--minutes/--seconds.")


def format_datetime(value: datetime, fmt: str) -> str:
    return value.strftime(fmt)


def duration(start: ParsedTime, end: ParsedTime) -> DurationResult:
    return DurationResult(end.value - start.value)


def add_time(start: ParsedTime, adjustment: TimeAdjustment) -> datetime:
    ensure_any_adjustment(adjustment)
    return start.value + adjustment.to_timedelta()


def subtract_time(start: ParsedTime, adjustment: TimeAdjustment) -> datetime:
    ensure_any_adjustment(adjustment)
    return start.value - adjustment.to_timedelta()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Calculate time durations and adjustments.")
    parser.add_argument(
        "--format",
        default=DEFAULT_FORMAT,
        help=f"Datetime format (default: {DEFAULT_FORMAT})",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    duration_parser = subparsers.add_parser("duration", help="Calculate duration between two times.")
    duration_parser.add_argument("--start", required=True, help="Start datetime string.")
    duration_parser.add_argument("--end", required=True, help="End datetime string.")
    duration_parser.add_argument("--human", action="store_true", help="Output a human-readable duration.")

    add_parser = subparsers.add_parser("add", help="Add a duration to a start time.")
    add_parser.add_argument("--start", required=True, help="Start datetime string.")
    add_parser.add_argument("--hours", type=int, default=0)
    add_parser.add_argument("--minutes", type=int, default=0)
    add_parser.add_argument("--seconds", type=int, default=0)

    subtract_parser = subparsers.add_parser("subtract", help="Subtract a duration from a start time.")
    subtract_parser.add_argument("--start", required=True, help="Start datetime string.")
    subtract_parser.add_argument("--hours", type=int, default=0)
    subtract_parser.add_argument("--minutes", type=int, default=0)
    subtract_parser.add_argument("--seconds", type=int, default=0)

    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    fmt = args.format

    if args.command == "duration":
        start = parse_time(args.start, fmt)
        end = parse_time(args.end, fmt)
        result = duration(start, end)
        output = result.to_human() if args.human else result.to_hms()
        print(output)
        return 0

    start = parse_time(args.start, fmt)
    adjustment = TimeAdjustment(hours=args.hours, minutes=args.minutes, seconds=args.seconds)

    if args.command == "add":
        result_time = add_time(start, adjustment)
    elif args.command == "subtract":
        result_time = subtract_time(start, adjustment)
    else:
        raise SystemExit("Unknown command.")

    print(format_datetime(result_time, fmt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
