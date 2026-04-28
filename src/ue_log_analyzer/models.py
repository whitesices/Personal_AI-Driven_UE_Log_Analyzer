from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class LogFileInfo:
    project_root: Path
    log_path: Path
    size_bytes: int
    modified_time: datetime
    read_limit_chars: int
    chars_read: int
    was_truncated: bool

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["project_root"] = str(self.project_root)
        data["log_path"] = str(self.log_path)
        data["modified_time"] = self.modified_time.isoformat()
        return data


@dataclass(frozen=True)
class DetectedLine:
    line_number: int
    text: str
    matched_keywords: tuple[str, ...]


@dataclass(frozen=True)
class LogIssue:
    category: str
    severity: str
    line_number: int
    message: str
    matched_keywords: tuple[str, ...]
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["matched_keywords"] = list(self.matched_keywords)
        return data


@dataclass(frozen=True)
class AnalysisSummary:
    total_issues: int
    severity_counts: dict[str, int]
    category_counts: dict[str, int]
    keyword_counts: dict[str, int]
    has_blocking_issue: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AnalysisResult:
    analyzed_at: datetime
    log_info: LogFileInfo
    summary: AnalysisSummary
    issues: list[LogIssue] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "analyzed_at": self.analyzed_at.isoformat(),
            "log_info": self.log_info.to_dict(),
            "summary": self.summary.to_dict(),
            "issues": [issue.to_dict() for issue in self.issues],
        }


def utc_now() -> datetime:
    return datetime.now(timezone.utc)

