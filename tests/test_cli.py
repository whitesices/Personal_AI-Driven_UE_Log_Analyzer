from __future__ import annotations

from pathlib import Path

import pytest

from ue_log_analyzer.cli import main


def make_project(workspace: Path) -> Path:
    project = workspace / "Project"
    logs = project / "Saved" / "Logs"
    plugin = project / "Plugins" / "DemoPlugin"
    logs.mkdir(parents=True)
    plugin.mkdir(parents=True)
    (project / "Project.uproject").write_text(
        '{"EngineAssociation":"5.3","Plugins":[{"Name":"DemoPlugin","Enabled":true}]}',
        encoding="utf-8",
    )
    (plugin / "DemoPlugin.uplugin").write_text(
        '{"EngineVersion":"5.1","Modules":[{"Name":"DemoRuntime","Type":"Runtime"}]}',
        encoding="utf-8",
    )
    (logs / "Project.log").write_text(
        "\n".join(
            [
                "LogTemp: Warning: safe warning",
                "LogBlueprint: Error: Compile of BP_Player failed. "
                "Could not find function GiveDamage.",
            ]
        ),
        encoding="utf-8",
    )
    return project


def test_cli_rejects_output_path_outside_project(workspace: Path) -> None:
    project = make_project(workspace)
    outside = workspace / "outside.md"

    with pytest.raises(SystemExit) as excinfo:
        main(["--project", str(project), "--output", str(outside)])

    assert excinfo.value.code == 2


def test_cli_accepts_project_relative_output_path(workspace: Path) -> None:
    project = make_project(workspace)

    exit_code = main(["--project", str(project), "--output", "AIReports/latest.md"])

    assert exit_code == 0
    assert (project / "AIReports" / "latest.md").exists()


def test_cli_full_diagnostics_appends_advanced_reports(workspace: Path) -> None:
    project = make_project(workspace)
    output = project / "AIReports" / "diagnostics.md"

    exit_code = main(
        [
            "--project",
            str(project),
            "--output",
            "AIReports/diagnostics.md",
            "--full-diagnostics",
        ]
    )

    assert exit_code == 0
    report = output.read_text(encoding="utf-8")
    assert "# UE Plugin Compatibility Report" in report
    assert "# UE Blueprint Error Analysis" in report
    assert "# UE Auto Fix Suggestion Plan" in report


def test_cli_advanced_diagnostics_respect_explicit_log_path(workspace: Path) -> None:
    project = make_project(workspace)
    specific_log = project / "Saved" / "Logs" / "Specific.log"
    specific_log.write_text(
        "LogBlueprint: Error: Compile of BP_Specific failed. "
        "Could not find function UseItem.",
        encoding="utf-8",
    )

    exit_code = main(
        [
            "--project",
            str(project),
            "--log-path",
            "Saved/Logs/Specific.log",
            "--output",
            "AIReports/specific.md",
            "--blueprint-analysis",
            "--fix-plan",
        ]
    )

    assert exit_code == 0
    report = (project / "AIReports" / "specific.md").read_text(encoding="utf-8")
    assert "BP_Specific" in report
    assert "UseItem" in report
