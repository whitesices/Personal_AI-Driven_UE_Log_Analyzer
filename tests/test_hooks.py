from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def load_hook(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[path.stem] = module
    spec.loader.exec_module(module)
    return module


def test_after_code_change_builds_pytest_command() -> None:
    hook = load_hook(Path("hooks") / "after_code_change.py")

    command = hook.build_pytest_command(["tests/test_reader.py"])

    assert command[0] == sys.executable
    assert command[1:3] == ["-m", "pytest"]
    assert command[-1] == "tests/test_reader.py"


def test_pre_commit_scan_returns_blocking_status(workspace: Path) -> None:
    hook = load_hook(Path("hooks") / "pre_commit_scan.py")
    project = workspace / "Project"
    logs = project / "Saved" / "Logs"
    logs.mkdir(parents=True)
    (logs / "Project.log").write_text(
        "Fatal error: Assertion failed: Something broke",
        encoding="utf-8",
    )

    assert hook.scan_project(str(project)) == 1


def test_pre_commit_scan_returns_success_for_clean_log(workspace: Path) -> None:
    hook = load_hook(Path("hooks") / "pre_commit_scan.py")
    project = workspace / "Project"
    logs = project / "Saved" / "Logs"
    logs.mkdir(parents=True)
    (logs / "Project.log").write_text("LogTemp: Display: clean", encoding="utf-8")

    assert hook.scan_project(str(project)) == 0
