from __future__ import annotations

from pathlib import Path

import pytest

from ue_log_analyzer.cli import main


def make_project(workspace: Path) -> Path:
    project = workspace / "Project"
    logs = project / "Saved" / "Logs"
    logs.mkdir(parents=True)
    (logs / "Project.log").write_text("LogTemp: Warning: safe warning", encoding="utf-8")
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

