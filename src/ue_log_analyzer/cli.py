from __future__ import annotations

import argparse
from pathlib import Path

from .analyzer import analyze_project
from .reader import DEFAULT_READ_LIMIT_CHARS, LogReaderError
from .report import render_markdown_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze the latest Unreal Engine log.")
    parser.add_argument("project_root", help="Path to the UE project root directory.")
    parser.add_argument(
        "--log-path",
        help="Optional explicit log path. Must be inside the UE project directory.",
    )
    parser.add_argument(
        "--read-limit-chars",
        type=int,
        default=DEFAULT_READ_LIMIT_CHARS,
        help="Maximum number of trailing characters to analyze.",
    )
    parser.add_argument(
        "--output",
        help="Optional Markdown output path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = analyze_project(
            project_root=args.project_root,
            log_path=args.log_path,
            read_limit_chars=args.read_limit_chars,
        )
        report = render_markdown_report(result)
    except LogReaderError as exc:
        parser.error(str(exc))
        return 2

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(report, encoding="utf-8")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

