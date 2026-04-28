from __future__ import annotations

import os
from pathlib import Path

import pytest

from ue_log_analyzer.reader import LogReaderError, find_latest_log, read_log_tail


def make_ue_project(workspace: Path) -> Path:
    project = workspace / "MyGame"
    (project / "Saved" / "Logs").mkdir(parents=True)
    return project


def test_find_latest_log_uses_modified_time(workspace: Path) -> None:
    project = make_ue_project(workspace)
    older = project / "Saved" / "Logs" / "older.log"
    newer = project / "Saved" / "Logs" / "newer.log"
    older.write_text("old", encoding="utf-8")
    newer.write_text("new", encoding="utf-8")
    os.utime(older, (100, 100))
    os.utime(newer, (200, 200))

    assert find_latest_log(project) == newer.resolve()


def test_read_log_tail_limits_content(workspace: Path) -> None:
    project = make_ue_project(workspace)
    log_path = project / "Saved" / "Logs" / "game.log"
    log_path.write_text("a" * 50 + "TAIL", encoding="utf-8")

    result = read_log_tail(project, read_limit_chars=10)

    assert result.content == "aaaaaaTAIL"
    assert result.info.chars_read == 10
    assert result.info.was_truncated is True


def test_read_log_tail_accepts_project_relative_log_path(workspace: Path) -> None:
    project = make_ue_project(workspace)
    log_path = project / "Saved" / "Logs" / "game.log"
    log_path.write_text("Error: relative path works", encoding="utf-8")

    result = read_log_tail(project, log_path=Path("Saved") / "Logs" / "game.log")

    assert "relative path works" in result.content


def test_read_log_tail_rejects_path_outside_project(workspace: Path) -> None:
    project = make_ue_project(workspace)
    outside = workspace / "outside.log"
    outside.write_text("Error: should not be read", encoding="utf-8")

    with pytest.raises(LogReaderError, match="outside UE project"):
        read_log_tail(project, log_path=outside)


def test_read_log_tail_errors_when_no_logs_exist(workspace: Path) -> None:
    project = make_ue_project(workspace)

    with pytest.raises(LogReaderError, match="No .log files"):
        read_log_tail(project)
