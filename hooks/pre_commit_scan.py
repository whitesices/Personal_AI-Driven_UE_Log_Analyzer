from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ue_log_analyzer.analyzer import BLOCKING_SEVERITIES, analyze_project
from ue_log_analyzer.reader import DEFAULT_READ_LIMIT_CHARS, LogReaderError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scan the latest UE log before commit.")
    parser.add_argument(
        "project_root",
        nargs="?",
        help="UE project root. Falls back to UE_PROJECT_ROOT environment variable.",
    )
    parser.add_argument(
        "--read-limit-chars",
        type=int,
        default=DEFAULT_READ_LIMIT_CHARS,
        help="Maximum number of trailing log characters to analyze.",
    )
    return parser


def scan_project(project_root: str, read_limit_chars: int = DEFAULT_READ_LIMIT_CHARS) -> int:
    try:
        result = analyze_project(
            project_root=project_root,
            read_limit_chars=read_limit_chars,
        )
    except LogReaderError as exc:
        print(f"UE log scan failed: {exc}", file=sys.stderr)
        return 2

    blocking = [
        issue for issue in result.issues if issue.severity in BLOCKING_SEVERITIES
    ]
    print(
        "UE log scan: "
        f"{result.summary.total_issues} issue(s), "
        f"blocking={len(blocking)}, "
        f"log={result.log_info.log_path}"
    )
    for issue in blocking[:10]:
        print(
            f"- line {issue.line_number}: {issue.severity}/{issue.category}: "
            f"{issue.message}"
        )
    return 1 if blocking else 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    project_root = args.project_root or os.environ.get("UE_PROJECT_ROOT")
    if not project_root:
        print(
            "UE project root is required. Pass it as an argument or set UE_PROJECT_ROOT.",
            file=sys.stderr,
        )
        return 2
    return scan_project(project_root, args.read_limit_chars)


if __name__ == "__main__":
    raise SystemExit(main())

