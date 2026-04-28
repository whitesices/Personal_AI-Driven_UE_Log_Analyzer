from __future__ import annotations

from pathlib import Path
from typing import Any

from .reader import (
    LogReaderError,
    ensure_within_project,
    find_latest_log,
    resolve_project_root,
)

IMPORTANT_DIRECTORIES = (
    "Config",
    "Content",
    "Plugins",
    "Saved",
    "Saved/Logs",
    "Source",
    "Intermediate",
)


def scan_project_structure(project_root: str | Path) -> dict[str, Any]:
    """Scan high-level UE project structure without reading files outside project_root."""
    root = resolve_project_root(project_root)
    uproject_files = _relative_paths(_safe_glob(root, "*.uproject"), root)
    plugin_descriptors = _relative_paths(_safe_rglob(root / "Plugins", "*.uplugin", root), root)

    latest_log: str | None
    try:
        latest_log = find_latest_log(root).relative_to(root).as_posix()
    except LogReaderError:
        latest_log = None

    return {
        "project_root": str(root),
        "uproject_files": uproject_files,
        "plugin_descriptors": plugin_descriptors,
        "directory_presence": {
            directory: (root / Path(directory)).exists() for directory in IMPORTANT_DIRECTORIES
        },
        "latest_log": latest_log,
    }


def _safe_glob(root: Path, pattern: str) -> list[Path]:
    return [
        ensure_within_project(path, root)
        for path in root.glob(pattern)
        if path.is_file()
    ]


def _safe_rglob(start: Path, pattern: str, root: Path) -> list[Path]:
    if not start.exists() or not start.is_dir():
        return []
    results: list[Path] = []
    for path in start.rglob(pattern):
        safe_path = ensure_within_project(path, root)
        if safe_path.is_file():
            results.append(safe_path)
    return results


def _relative_paths(paths: list[Path], root: Path) -> list[str]:
    return [path.relative_to(root).as_posix() for path in sorted(paths)]
