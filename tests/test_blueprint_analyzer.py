from __future__ import annotations

from pathlib import Path

from ue_log_analyzer.blueprint_analyzer import analyze_blueprint_errors


def test_blueprint_analyzer_extracts_compile_error_and_missing_symbol(
    workspace: Path,
) -> None:
    project = workspace / "Project"
    logs = project / "Saved" / "Logs"
    logs.mkdir(parents=True)
    (logs / "Project.log").write_text(
        "LogBlueprint: Error: Compile of BP_Player failed. "
        "Could not find function GiveDamage.",
        encoding="utf-8",
    )

    report = analyze_blueprint_errors(project)

    assert report.total_errors == 1
    insight = report.insights[0]
    assert insight.blueprint_name == "BP_Player"
    assert insight.error_type == "compile_failed"
    assert insight.missing_symbol == "GiveDamage"
    assert "Blueprint" in insight.likely_stage


def test_blueprint_analyzer_detects_runtime_accessed_none(workspace: Path) -> None:
    project = workspace / "Project"
    logs = project / "Saved" / "Logs"
    logs.mkdir(parents=True)
    (logs / "Project.log").write_text(
        "Blueprint Runtime Error: Accessed None trying to read property TargetActor",
        encoding="utf-8",
    )

    report = analyze_blueprint_errors(project)

    assert report.total_errors == 1
    insight = report.insights[0]
    assert insight.error_type == "accessed_none"
    assert insight.likely_stage == "Runtime/PIE"
    assert any("validity checks" in fix for fix in insight.recommended_fixes)
