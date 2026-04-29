from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .analyzer import analyze_project
from .blueprint_analyzer import analyze_blueprint_errors
from .plugin_checker import check_plugin_compatibility
from .reader import DEFAULT_READ_LIMIT_CHARS


@dataclass(frozen=True)
class FixSuggestion:
    priority: int
    title: str
    category: str
    risk_level: str
    rationale: str
    actions: tuple[str, ...]
    verification_steps: tuple[str, ...]
    safety_notes: tuple[str, ...] = (
        "This agent only suggests fixes; it does not modify UE project files.",
    )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["actions"] = list(self.actions)
        data["verification_steps"] = list(self.verification_steps)
        data["safety_notes"] = list(self.safety_notes)
        return data


@dataclass(frozen=True)
class AutoFixPlan:
    project_root: Path
    suggestions: list[FixSuggestion] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_root": str(self.project_root),
            "suggestions": [suggestion.to_dict() for suggestion in self.suggestions],
        }


def generate_auto_fix_plan(
    project_root: str | Path,
    log_path: str | Path | None = None,
    read_limit_chars: int = DEFAULT_READ_LIMIT_CHARS,
) -> AutoFixPlan:
    """Generate a deterministic, non-mutating fix plan from log and project diagnostics."""
    analysis = analyze_project(project_root, log_path=log_path, read_limit_chars=read_limit_chars)
    plugin_report = check_plugin_compatibility(project_root)
    blueprint_report = analyze_blueprint_errors(
        project_root,
        log_path=log_path,
        read_limit_chars=read_limit_chars,
    )

    suggestions: list[FixSuggestion] = []
    suggestions.extend(_suggest_from_log_issues(analysis.issues))
    suggestions.extend(_suggest_from_plugin_issues(plugin_report.issues))
    suggestions.extend(_suggest_from_blueprint_insights(blueprint_report.insights))

    deduped = _dedupe_suggestions(suggestions)
    deduped.sort(key=lambda suggestion: (suggestion.priority, suggestion.title))
    return AutoFixPlan(project_root=analysis.log_info.project_root, suggestions=deduped[:10])


def _suggest_from_log_issues(issues: list[Any]) -> list[FixSuggestion]:
    suggestions: list[FixSuggestion] = []
    for issue in issues:
        if issue.severity not in {"critical", "high"}:
            continue
        suggestions.append(
            FixSuggestion(
                priority=_priority(issue.severity),
                title=f"Address {issue.category} from latest UE log",
                category=issue.category,
                risk_level=issue.risk_level,
                rationale=issue.explanation,
                actions=issue.recommended_fixes or ("Inspect the latest log evidence.",),
                verification_steps=issue.verification_steps
                or ("Rerun the failing UE workflow and analyze the latest log.",),
            )
        )
    return suggestions


def _suggest_from_plugin_issues(plugin_issues: list[Any]) -> list[FixSuggestion]:
    return [
        FixSuggestion(
            priority=_priority(issue.severity),
            title=f"Fix plugin compatibility issue: {issue.plugin_name}",
            category="plugin_compatibility",
            risk_level=issue.severity,
            rationale=issue.message,
            actions=issue.recommended_fixes,
            verification_steps=issue.verification_steps,
        )
        for issue in plugin_issues
    ]


def _suggest_from_blueprint_insights(blueprint_insights: list[Any]) -> list[FixSuggestion]:
    suggestions: list[FixSuggestion] = []
    for insight in blueprint_insights:
        title_target = insight.blueprint_name or "Blueprint"
        suggestions.append(
            FixSuggestion(
                priority=30,
                title=f"Repair Blueprint issue: {title_target}",
                category="blueprint_error",
                risk_level="medium",
                rationale=insight.message,
                actions=insight.recommended_fixes,
                verification_steps=insight.verification_steps,
            )
        )
    return suggestions


def _dedupe_suggestions(suggestions: list[FixSuggestion]) -> list[FixSuggestion]:
    seen: set[tuple[str, str]] = set()
    deduped: list[FixSuggestion] = []
    for suggestion in suggestions:
        key = (suggestion.title, suggestion.category)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(suggestion)
    return deduped


def _priority(severity: str) -> int:
    priorities = {
        "critical": 10,
        "high": 20,
        "medium": 30,
        "low": 40,
    }
    return priorities.get(severity, 50)
