from __future__ import annotations

import argparse
from pathlib import Path

from .analyzer import analyze_project
from .reader import (
    DEFAULT_READ_LIMIT_CHARS,
    LogReaderError,
    ensure_within_project,
    resolve_project_root,
)
from .report import render_markdown_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze the latest Unreal Engine log under a UE project Saved/Logs folder.",
        epilog=(
            "Examples:\n"
            "  python -m ue_log_analyzer --project D:/UEProjects/MyProject\n"
            "  python -m ue_log_analyzer --project D:/UEProjects/MyProject "
            "--output AIReports/latest_report.md\n"
            "  ue-log-analyzer D:/UEProjects/MyProject --log-path Saved/Logs/MyProject.log"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "project_root",
        nargs="?",
        help="Path to the UE project root directory. Kept for backward compatibility.",
    )
    parser.add_argument(
        "--project",
        help="Path to the UE project root directory. Preferred explicit form.",
    )
    parser.add_argument(
        "--log-path",
        help=(
            "Optional explicit log path. Relative paths are resolved inside the UE project "
            "directory and absolute paths must also stay inside it."
        ),
    )
    parser.add_argument(
        "--read-limit-chars",
        type=int,
        default=DEFAULT_READ_LIMIT_CHARS,
        help="Maximum number of trailing characters to analyze.",
    )
    parser.add_argument(
        "--output",
        help=(
            "Optional Markdown output path. Relative paths are resolved inside the UE project "
            "directory. Absolute paths outside the project are rejected."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    project_root = args.project or args.project_root
    if not project_root:
        parser.error("UE project root is required. Use --project or the positional argument.")
        return 2

    try:
        root = resolve_project_root(project_root)
        result = analyze_project(
            project_root=root,
            log_path=args.log_path,
            read_limit_chars=args.read_limit_chars,
        )
        report = render_markdown_report(result)
        output_path = _resolve_output_path(root, args.output) if args.output else None
    except LogReaderError as exc:
        parser.error(str(exc))
        return 2

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
    else:
        print(report)
    return 0


def _resolve_output_path(project_root: Path, output: str) -> Path:
    requested_output = Path(output).expanduser()
    if not requested_output.is_absolute():
        requested_output = project_root / requested_output
    return ensure_within_project(requested_output, project_root)


if __name__ == "__main__":
    raise SystemExit(main())
