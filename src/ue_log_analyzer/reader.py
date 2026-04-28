from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .models import LogFileInfo

DEFAULT_READ_LIMIT_CHARS = 20_000
DEFAULT_LOG_DIR = Path("Saved") / "Logs"


class LogReaderError(RuntimeError):
    """Raised when a UE log cannot be found or safely read."""


@dataclass(frozen=True)
class ReadLogResult:
    info: LogFileInfo
    content: str


def resolve_project_root(project_root: str | Path) -> Path:
    root = Path(project_root).expanduser().resolve()
    if not root.exists():
        raise LogReaderError(f"UE project directory does not exist: {root}")
    if not root.is_dir():
        raise LogReaderError(f"UE project path is not a directory: {root}")
    return root


def is_within_directory(candidate: Path, root: Path) -> bool:
    candidate_resolved = candidate.expanduser().resolve()
    root_resolved = root.expanduser().resolve()
    try:
        candidate_resolved.relative_to(root_resolved)
        return True
    except ValueError:
        return False


def ensure_within_project(candidate: Path, project_root: Path) -> Path:
    candidate_resolved = candidate.expanduser().resolve()
    if not is_within_directory(candidate_resolved, project_root):
        raise LogReaderError(
            f"Refusing to read path outside UE project directory: {candidate_resolved}"
        )
    return candidate_resolved


def get_logs_dir(project_root: str | Path) -> Path:
    root = resolve_project_root(project_root)
    logs_dir = ensure_within_project(root / DEFAULT_LOG_DIR, root)
    if not logs_dir.exists():
        raise LogReaderError(f"UE logs directory does not exist: {logs_dir}")
    if not logs_dir.is_dir():
        raise LogReaderError(f"UE logs path is not a directory: {logs_dir}")
    return logs_dir


def find_latest_log(project_root: str | Path) -> Path:
    root = resolve_project_root(project_root)
    logs_dir = get_logs_dir(root)
    candidates = [
        ensure_within_project(path, root)
        for path in logs_dir.glob("*.log")
        if path.is_file()
    ]
    if not candidates:
        raise LogReaderError(f"No .log files found in UE logs directory: {logs_dir}")
    return max(candidates, key=lambda path: path.stat().st_mtime)


def read_log_tail(
    project_root: str | Path,
    log_path: str | Path | None = None,
    read_limit_chars: int = DEFAULT_READ_LIMIT_CHARS,
) -> ReadLogResult:
    if read_limit_chars <= 0:
        raise LogReaderError("read_limit_chars must be greater than 0")

    root = resolve_project_root(project_root)
    selected_log = find_latest_log(root) if log_path is None else Path(log_path)
    if not selected_log.is_absolute():
        selected_log = root / selected_log
    selected_log = ensure_within_project(selected_log, root)
    if not selected_log.exists():
        raise LogReaderError(f"Log file does not exist: {selected_log}")
    if not selected_log.is_file():
        raise LogReaderError(f"Log path is not a file: {selected_log}")

    stat = selected_log.stat()
    tail, was_truncated = _read_tail_text(selected_log, stat.st_size, read_limit_chars)
    info = LogFileInfo(
        project_root=root,
        log_path=selected_log,
        size_bytes=stat.st_size,
        modified_time=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
        read_limit_chars=read_limit_chars,
        chars_read=len(tail),
        was_truncated=was_truncated,
    )
    return ReadLogResult(info=info, content=tail)


def _read_tail_text(log_path: Path, size_bytes: int, read_limit_chars: int) -> tuple[str, bool]:
    byte_window = min(size_bytes, max(read_limit_chars * 4, read_limit_chars))
    with log_path.open("rb") as file:
        if byte_window < size_bytes:
            file.seek(-byte_window, 2)
        raw_tail = file.read(byte_window)
    decoded_tail = raw_tail.decode("utf-8", errors="replace")
    was_truncated = byte_window < size_bytes or len(decoded_tail) > read_limit_chars
    return decoded_tail[-read_limit_chars:], was_truncated
