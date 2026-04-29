from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from .analyzer import analyze_project
from .auto_fix_agent import generate_auto_fix_plan
from .blueprint_analyzer import analyze_blueprint_errors
from .plugin_checker import check_plugin_compatibility
from .project_scanner import scan_project_structure
from .reader import (
    DEFAULT_READ_LIMIT_CHARS,
    LogReaderError,
    ensure_within_project,
    find_latest_log,
    read_log_tail,
    resolve_project_root,
)
from .report import render_markdown_report

ToolHandler = Callable[..., dict[str, Any]]


def get_latest_log_info(project_root: str) -> dict[str, Any]:
    """Return metadata for the newest UE log under Saved/Logs."""
    try:
        latest_log = find_latest_log(project_root)
        read_result = read_log_tail(project_root, latest_log, read_limit_chars=1)
        return {
            "ok": True,
            "log_info": read_result.info.to_dict(),
        }
    except LogReaderError as exc:
        return _error(str(exc))


def analyze_latest_log(
    project_root: str,
    read_limit_chars: int = DEFAULT_READ_LIMIT_CHARS,
) -> dict[str, Any]:
    """Analyze the newest UE log and return JSON-serializable data."""
    try:
        result = analyze_project(
            project_root=project_root,
            read_limit_chars=read_limit_chars,
        )
        return {
            "ok": True,
            "analysis": result.to_dict(),
        }
    except LogReaderError as exc:
        return _error(str(exc))


def generate_markdown_report(
    project_root: str,
    read_limit_chars: int = DEFAULT_READ_LIMIT_CHARS,
) -> dict[str, Any]:
    """Analyze the newest UE log and return a Markdown report."""
    try:
        result = analyze_project(
            project_root=project_root,
            read_limit_chars=read_limit_chars,
        )
        return {
            "ok": True,
            "report": render_markdown_report(result),
            "analysis": result.to_dict(),
        }
    except LogReaderError as exc:
        return _error(str(exc))


def scan_ue_project_structure(project_root: str) -> dict[str, Any]:
    """Return high-level UE project structure without reading outside project_root."""
    try:
        return {
            "ok": True,
            "project_structure": scan_project_structure(project_root),
        }
    except LogReaderError as exc:
        return _error(str(exc))


def check_ue_plugin_compatibility(project_root: str) -> dict[str, Any]:
    """Check UE plugin descriptors for version and module compatibility risks."""
    try:
        return {
            "ok": True,
            "plugin_compatibility": check_plugin_compatibility(project_root).to_dict(),
        }
    except LogReaderError as exc:
        return _error(str(exc))


def analyze_ue_blueprint_errors(
    project_root: str,
    read_limit_chars: int = DEFAULT_READ_LIMIT_CHARS,
) -> dict[str, Any]:
    """Analyze latest UE log for Blueprint compile and runtime errors."""
    try:
        return {
            "ok": True,
            "blueprint_analysis": analyze_blueprint_errors(
                project_root,
                read_limit_chars=read_limit_chars,
            ).to_dict(),
        }
    except LogReaderError as exc:
        return _error(str(exc))


def generate_ue_auto_fix_plan(
    project_root: str,
    read_limit_chars: int = DEFAULT_READ_LIMIT_CHARS,
) -> dict[str, Any]:
    """Generate a non-mutating fix suggestion plan from UE diagnostics."""
    try:
        return {
            "ok": True,
            "auto_fix_plan": generate_auto_fix_plan(
                project_root,
                read_limit_chars=read_limit_chars,
            ).to_dict(),
        }
    except LogReaderError as exc:
        return _error(str(exc))


def write_markdown_report(
    project_root: str,
    output_path: str,
    read_limit_chars: int = DEFAULT_READ_LIMIT_CHARS,
) -> dict[str, Any]:
    """Write a Markdown report inside the UE project directory or current workspace."""
    report_result = generate_markdown_report(project_root, read_limit_chars)
    if not report_result["ok"]:
        return report_result

    try:
        root = resolve_project_root(project_root)
        requested_output = Path(output_path).expanduser()
        if not requested_output.is_absolute():
            requested_output = root / requested_output
        destination = ensure_within_project(requested_output, root)
    except LogReaderError as exc:
        return _error(str(exc))

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(str(report_result["report"]), encoding="utf-8")
    return {
        "ok": True,
        "output_path": str(destination),
        "analysis": report_result["analysis"],
    }


def tool_manifest() -> dict[str, Any]:
    """Describe available MCP-style tools without binding to a specific runtime."""
    return {
        "server_name": "ai-driven-ue-log-analyzer",
        "tools": [
            {
                "name": "get_latest_log_info",
                "description": "Return metadata for the newest Unreal Engine log under Saved/Logs.",
                "input_schema": {"project_root": "string"},
            },
            {
                "name": "analyze_latest_log",
                "description": "Analyze the newest UE log and return structured issue data.",
                "input_schema": {
                    "project_root": "string",
                    "read_limit_chars": "integer optional",
                },
            },
            {
                "name": "generate_markdown_report",
                "description": "Analyze the newest UE log and return a Markdown report.",
                "input_schema": {
                    "project_root": "string",
                    "read_limit_chars": "integer optional",
                },
            },
            {
                "name": "scan_ue_project_structure",
                "description": (
                    "Return high-level UE project folders, .uproject files, "
                    "plugins, and latest log."
                ),
                "input_schema": {"project_root": "string"},
            },
            {
                "name": "check_ue_plugin_compatibility",
                "description": "Check UE plugin descriptors for compatibility risks.",
                "input_schema": {"project_root": "string"},
            },
            {
                "name": "analyze_ue_blueprint_errors",
                "description": "Analyze the newest UE log for Blueprint errors.",
                "input_schema": {
                    "project_root": "string",
                    "read_limit_chars": "integer optional",
                },
            },
            {
                "name": "generate_ue_auto_fix_plan",
                "description": "Generate a safe, non-mutating UE fix suggestion plan.",
                "input_schema": {
                    "project_root": "string",
                    "read_limit_chars": "integer optional",
                },
            },
        ],
    }


def dispatch_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Small dispatcher useful for MCP adapters and tests."""
    tools: dict[str, ToolHandler] = {
        "get_latest_log_info": get_latest_log_info,
        "analyze_latest_log": analyze_latest_log,
        "generate_markdown_report": generate_markdown_report,
        "scan_ue_project_structure": scan_ue_project_structure,
        "check_ue_plugin_compatibility": check_ue_plugin_compatibility,
        "analyze_ue_blueprint_errors": analyze_ue_blueprint_errors,
        "generate_ue_auto_fix_plan": generate_ue_auto_fix_plan,
    }
    if name not in tools:
        return _error(f"Unknown tool: {name}")
    return tools[name](**arguments)


def main() -> int:
    print(json.dumps(tool_manifest(), ensure_ascii=False, indent=2))
    return 0


def _error(message: str) -> dict[str, Any]:
    return {
        "ok": False,
        "error": message,
    }


if __name__ == "__main__":
    raise SystemExit(main())
