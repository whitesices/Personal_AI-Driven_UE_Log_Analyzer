from __future__ import annotations

from pathlib import Path

from ue_log_analyzer.analyzer import analyze_project
from ue_log_analyzer.report import render_markdown_report


def test_markdown_report_has_required_sections(workspace: Path) -> None:
    project = workspace / "Game"
    logs = project / "Saved" / "Logs"
    logs.mkdir(parents=True)
    (logs / "Game.log").write_text(
        "PackagingResults: Error: Cook failed",
        encoding="utf-8",
    )

    report = render_markdown_report(analyze_project(project))

    assert "# UE Log Analysis Report" in report
    assert "## Metadata" in report
    assert "## Summary" in report
    assert "## High Priority Issues" in report
    assert "## Issues By Category" in report
    assert "## Evidence Snippets" in report
    assert "## Recommended Next Steps" in report
    assert "## Rule-Driven Action Plan" in report
    assert "packaging_error" in report


def test_markdown_report_promotes_rule_driven_action_plan(workspace: Path) -> None:
    project = workspace / "Game"
    logs = project / "Saved" / "Logs"
    logs.mkdir(parents=True)
    (logs / "Game.log").write_text(
        "Assertion failed: InSaver [File:Runtime/CoreUObject/Private/UObject/LinkerSave.cpp]",
        encoding="utf-8",
    )

    report = render_markdown_report(analyze_project(project))

    assert "## Rule-Driven Action Plan" in report
    assert "ue_savepackage_linkersave_assertion" in report
    assert "Verify the plugin version" in report
