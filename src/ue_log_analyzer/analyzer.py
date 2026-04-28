from __future__ import annotations

from collections import Counter
from pathlib import Path

from .classifier import classify_lines
from .detector import detect_issue_lines
from .models import AnalysisResult, AnalysisSummary, LogIssue, utc_now
from .reader import DEFAULT_READ_LIMIT_CHARS, read_log_tail

BLOCKING_SEVERITIES = {"critical", "high"}


def analyze_project(
    project_root: str | Path,
    log_path: str | Path | None = None,
    read_limit_chars: int = DEFAULT_READ_LIMIT_CHARS,
) -> AnalysisResult:
    read_result = read_log_tail(
        project_root=project_root,
        log_path=log_path,
        read_limit_chars=read_limit_chars,
    )
    detected_lines = detect_issue_lines(read_result.content)
    issues = classify_lines(detected_lines)
    summary = summarize_issues(issues)
    return AnalysisResult(
        analyzed_at=utc_now(),
        log_info=read_result.info,
        summary=summary,
        issues=issues,
    )


def summarize_issues(issues: list[LogIssue]) -> AnalysisSummary:
    severity_counts = Counter(issue.severity for issue in issues)
    category_counts = Counter(issue.category for issue in issues)
    keyword_counts: Counter[str] = Counter()
    for issue in issues:
        keyword_counts.update(issue.matched_keywords)

    return AnalysisSummary(
        total_issues=len(issues),
        severity_counts=dict(sorted(severity_counts.items())),
        category_counts=dict(sorted(category_counts.items())),
        keyword_counts=dict(sorted(keyword_counts.items())),
        has_blocking_issue=any(issue.severity in BLOCKING_SEVERITIES for issue in issues),
    )

