from __future__ import annotations

import argparse
from pathlib import Path

from .analyzer import analyze_project
from .auto_fix_agent import generate_auto_fix_plan
from .blueprint_analyzer import analyze_blueprint_errors
from .models import AnalysisResult
from .plugin_checker import check_plugin_compatibility
from .reader import (
    DEFAULT_READ_LIMIT_CHARS,
    LogReaderError,
    ensure_within_project,
    resolve_project_root,
)
from .report import (
    render_auto_fix_plan,
    render_blueprint_analysis_report,
    render_markdown_report,
    render_plugin_compatibility_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze the latest Unreal Engine log under a UE project Saved/Logs folder.",
        epilog=(
            "Examples:\n"
            "  python -m ue_log_analyzer --project D:/UEProjects/MyProject\n"
            "  python -m ue_log_analyzer --project D:/UEProjects/MyProject "
            "--output AIReports/latest_report.md\n"
            "  python -m ue_log_analyzer --project D:/UEProjects/MyProject "
            "--full-diagnostics\n"
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
    parser.add_argument(
        "--plugin-check",
        action="store_true",
        help="Append a UE plugin compatibility report based on .uproject and .uplugin files.",
    )
    parser.add_argument(
        "--blueprint-analysis",
        action="store_true",
        help="Append a Blueprint compile/runtime error analysis from the latest log.",
    )
    parser.add_argument(
        "--fix-plan",
        action="store_true",
        help="Append a safe, non-mutating UE auto fix suggestion plan.",
    )
    parser.add_argument(
        "--full-diagnostics",
        action="store_true",
        help="Enable plugin check, Blueprint analysis, and auto fix suggestions.",
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
        report = _build_report(root, result, args)
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


def _build_report(root: Path, result: AnalysisResult, args: argparse.Namespace) -> str:
    report_sections = [render_markdown_report(result)]
    plugin_check_enabled = bool(args.plugin_check or args.full_diagnostics)
    blueprint_enabled = bool(args.blueprint_analysis or args.full_diagnostics)
    fix_plan_enabled = bool(args.fix_plan or args.full_diagnostics)

    if plugin_check_enabled:
        report_sections.append(render_plugin_compatibility_report(check_plugin_compatibility(root)))
    if blueprint_enabled:
        report_sections.append(
            render_blueprint_analysis_report(
                analyze_blueprint_errors(
                    root,
                    log_path=args.log_path,
                    read_limit_chars=args.read_limit_chars,
                )
            )
        )
    if fix_plan_enabled:
        report_sections.append(
            render_auto_fix_plan(
                generate_auto_fix_plan(
                    root,
                    log_path=args.log_path,
                    read_limit_chars=args.read_limit_chars,
                )
            )
        )
    return "\n\n---\n\n".join(report_sections)


if __name__ == "__main__":
    raise SystemExit(main())
