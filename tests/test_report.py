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
    assert "packaging_error" in report
