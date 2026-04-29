from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from ue_log_analyzer.mcp_server import (
    analyze_latest_log,
    analyze_ue_blueprint_errors,
    check_ue_plugin_compatibility,
    dispatch_tool,
    generate_markdown_report,
    generate_ue_auto_fix_plan,
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
        '{"EngineVersion":"5.0","Modules":[{"Name":"DemoRuntime","Type":"Runtime"}]}',
        encoding="utf-8",
    )
    (logs / "Project.log").write_text(
        "\n".join(
            [
                "Source/Test.cpp(1): error C2143: syntax error",
                "LogBlueprint: Error: Compile of BP_Player failed. "
                "Could not find function GiveDamage.",
            ]
        ),
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


def test_mcp_plugin_compatibility_tool(workspace: Path) -> None:
    project = make_project(workspace)

    result = check_ue_plugin_compatibility(str(project))

    assert result["ok"] is True
    issues = result["plugin_compatibility"]["issues"]
    assert any(issue["issue_type"] == "module_missing" for issue in issues)


def test_mcp_blueprint_analysis_tool(workspace: Path) -> None:
    project = make_project(workspace)

    result = analyze_ue_blueprint_errors(str(project))

    assert result["ok"] is True
    insights = result["blueprint_analysis"]["insights"]
    assert insights[0]["blueprint_name"] == "BP_Player"
    assert insights[0]["missing_symbol"] == "GiveDamage"


def test_mcp_auto_fix_plan_tool(workspace: Path) -> None:
    project = make_project(workspace)

    result = generate_ue_auto_fix_plan(str(project))

    assert result["ok"] is True
    suggestions = result["auto_fix_plan"]["suggestions"]
    assert any(suggestion["category"] == "plugin_compatibility" for suggestion in suggestions)
    assert any(suggestion["category"] == "blueprint_error" for suggestion in suggestions)


def test_mcp_dispatches_new_diagnostic_tool(workspace: Path) -> None:
    project = make_project(workspace)

    result = dispatch_tool("analyze_ue_blueprint_errors", {"project_root": str(project)})

    assert result["ok"] is True
    assert result["blueprint_analysis"]["total_errors"] == 1


def test_mcp_stdio_registered_tools() -> None:
    assert registered_tool_names() == (
        "get_latest_log_info",
        "analyze_latest_log",
        "generate_markdown_report",
        "scan_ue_project_structure",
        "check_ue_plugin_compatibility",
        "analyze_ue_blueprint_errors",
        "generate_ue_auto_fix_plan",
    )


def test_mcp_stdio_create_server_when_sdk_available() -> None:
    if importlib.util.find_spec("mcp") is None:
        pytest.skip("MCP Python SDK is not installed")

    server = create_server()

    assert server is not None
