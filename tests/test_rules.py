from __future__ import annotations

from pathlib import Path

from ue_log_analyzer.analyzer import analyze_project
from ue_log_analyzer.rules import match_rules


def make_project(workspace: Path, content: str) -> Path:
    project = workspace / "Project"
    logs = project / "Saved" / "Logs"
    logs.mkdir(parents=True)
    (project / "Project.uproject").write_text("{}", encoding="utf-8")
    (logs / "Project.log").write_text(content, encoding="utf-8")
    return project


def test_rules_match_linkersave_insaver_hotpacher_case() -> None:
    matches = match_rules(
        "Assertion failed: InSaver [File:Runtime/CoreUObject/Private/UObject/LinkerSave.cpp] "
        "HotPatcher"
    )

    assert matches
    assert matches[0].rule_id == "ue_savepackage_linkersave_assertion"


def test_hotpacher_without_linkersave_or_insaver_does_not_match_critical_rule() -> None:
    matches = match_rules("LogHotPatcher: Display: patch settings loaded")

    assert all(rule.rule_id != "ue_savepackage_linkersave_assertion" for rule in matches)


def test_analyzer_enriches_linkersave_insaver_report(workspace: Path) -> None:
    project = make_project(
        workspace,
        "Assertion failed: InSaver [File:Runtime/CoreUObject/Private/UObject/LinkerSave.cpp] "
        "HotPatcher failed while SavePackage",
    )

    result = analyze_project(project)
    issue = result.issues[0]

    assert issue.rule_id == "ue_savepackage_linkersave_assertion"
    assert issue.likely_stage == "Cook/Package"
    assert issue.risk_level == "critical"
    assert any("plugin version" in fix.lower() for fix in issue.recommended_fixes)


def test_packagingresults_error_rule(workspace: Path) -> None:
    project = make_project(workspace, "PackagingResults: Error: Unknown Cook Failure")

    result = analyze_project(project)

    assert result.issues[0].category == "packaging_error"
    assert result.issues[0].severity == "high"
    assert result.issues[0].likely_stage == "Package"


def test_blueprint_compile_error_rule(workspace: Path) -> None:
    project = make_project(workspace, "LogBlueprint: Error: Compile of BP_Player failed")

    result = analyze_project(project)

    assert result.issues[0].category == "blueprint_error"
    assert result.issues[0].likely_stage == "Build/Cook/Runtime"


def test_missing_asset_rule(workspace: Path) -> None:
    project = make_project(workspace, "Failed to load object '/Game/Missing/Mesh01.Mesh01'")

    result = analyze_project(project)

    assert result.issues[0].category == "asset_reference_error"
    assert result.issues[0].likely_stage == "Load/Cook"
