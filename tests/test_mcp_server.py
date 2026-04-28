from __future__ import annotations

from pathlib import Path

from ue_log_analyzer.mcp_server import (
    analyze_latest_log,
    dispatch_tool,
    generate_markdown_report,
    get_latest_log_info,
)


def make_project(workspace: Path) -> Path:
    project = workspace / "Project"
    logs = project / "Saved" / "Logs"
    logs.mkdir(parents=True)
    (logs / "Project.log").write_text(
        "Source/Test.cpp(1): error C2143: syntax error",
        encoding="utf-8",
    )
    return project


def test_mcp_get_latest_log_info_returns_json_data(workspace: Path) -> None:
    project = make_project(workspace)

    result = get_latest_log_info(str(project))

    assert result["ok"] is True
    assert result["log_info"]["log_path"].endswith("Project.log")


def test_mcp_analyze_latest_log_returns_structured_result(workspace: Path) -> None:
    project = make_project(workspace)

    result = analyze_latest_log(str(project))

    assert result["ok"] is True
    assert result["analysis"]["summary"]["has_blocking_issue"] is True
    assert result["analysis"]["issues"][0]["category"] == "cpp_compile_error"


def test_mcp_generate_markdown_report_returns_report(workspace: Path) -> None:
    project = make_project(workspace)

    result = generate_markdown_report(str(project))

    assert result["ok"] is True
    assert "# UE Log Analysis Report" in result["report"]


def test_mcp_dispatch_rejects_unknown_tool() -> None:
    result = dispatch_tool("missing", {})

    assert result["ok"] is False
    assert "Unknown tool" in result["error"]
