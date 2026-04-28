from __future__ import annotations

from pathlib import Path

from ue_log_analyzer.analyzer import analyze_project


def make_project_with_log(workspace: Path, content: str) -> Path:
    project = workspace / "UEProject"
    logs = project / "Saved" / "Logs"
    logs.mkdir(parents=True)
    (logs / "UEProject.log").write_text(content, encoding="utf-8")
    return project


def test_analyze_project_classifies_common_ue_failures(workspace: Path) -> None:
    project = make_project_with_log(
        workspace,
        "\n".join(
            [
                "LogInit: Display: start",
                "PackagingResults: Error: Unknown Cook Failure",
                "LogBlueprint: Error: Failed to compile BP_Player",
                "Source/MyActor.cpp(42): error C2143: syntax error",
                "Fatal error: Assertion failed: Object != nullptr",
                "LogLinker: Warning: Can't find file '/Game/MissingAsset'",
                "LogPluginManager: Error: Plugin Foo failed to load",
            ]
        ),
    )

    result = analyze_project(project)
    categories = {issue.category for issue in result.issues}
    severities = {issue.severity for issue in result.issues}

    assert result.summary.total_issues == 6
    assert result.summary.has_blocking_issue is True
    assert "packaging_error" in categories
    assert "blueprint_error" in categories
    assert "cpp_compile_error" in categories
    assert "runtime_crash" in categories
    assert "asset_reference_error" in categories
    assert "plugin_compatibility" in categories
    assert "critical" in severities
    assert "high" in severities


def test_analyze_project_handles_clean_log(workspace: Path) -> None:
    project = make_project_with_log(
        workspace,
        "LogInit: Display: Engine started\nLogTemp: Display: Everything okay",
    )

    result = analyze_project(project)

    assert result.summary.total_issues == 0
    assert result.summary.has_blocking_issue is False
    assert result.issues == []
