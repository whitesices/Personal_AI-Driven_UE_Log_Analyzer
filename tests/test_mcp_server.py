from __future__ import annotations

from pathlib import Path

from ue_log_analyzer.mcp_server import (
    analyze_latest_log,
    dispatch_tool,
    generate_markdown_report,
    get_latest_log_info,
    scan_ue_project_structure,
)
from ue_log_analyzer.mcp_stdio_server import create_server, registered_tool_names


def make_project(workspace: Path) -> Path:
    project = workspace / "Project"
    logs = project / "Saved" / "Logs"
    logs.mkdir(parents=True)
    (project / "Project.uproject").write_text("{}", encoding="utf-8")
    (project / "Source").mkdir()
    (project / "Content").mkdir()
    (project / "Plugins" / "DemoPlugin").mkdir(parents=True)
    (project / "Plugins" / "DemoPlugin" / "DemoPlugin.uplugin").write_text(
        "{}",
        encoding="utf-8",
    )
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


def test_mcp_scan_ue_project_structure(workspace: Path) -> None:
    project = make_project(workspace)

    result = scan_ue_project_structure(str(project))

    assert result["ok"] is True
    structure = result["project_structure"]
    assert structure["uproject_files"] == ["Project.uproject"]
    assert structure["directory_presence"]["Source"] is True
    assert structure["plugin_descriptors"] == ["Plugins/DemoPlugin/DemoPlugin.uplugin"]


def test_mcp_stdio_registered_tools() -> None:
    assert registered_tool_names() == (
        "get_latest_log_info",
        "analyze_latest_log",
        "generate_markdown_report",
        "scan_ue_project_structure",
    )


def test_mcp_stdio_create_server_when_sdk_available() -> None:
    server = create_server()

    assert server is not None
