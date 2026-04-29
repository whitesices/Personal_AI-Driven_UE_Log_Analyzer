from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .reader import DEFAULT_READ_LIMIT_CHARS, read_log_tail

BLUEPRINT_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("compile_failed", re.compile(r"Compile of (?P<name>[\w./-]+) failed", re.IGNORECASE)),
    ("log_blueprint_error", re.compile(r"LogBlueprint:\s*Error:\s*(?P<detail>.+)", re.IGNORECASE)),
    ("runtime_error", re.compile(r"Blueprint Runtime Error:\s*(?P<detail>.+)", re.IGNORECASE)),
    ("k2node_warning", re.compile(r"K2Node_[\w]+:\s*(?P<detail>.+)", re.IGNORECASE)),
    (
        "missing_function",
        re.compile(
            r"(Could not find function|missing function)\s+(?P<symbol>[\w:]+)",
            re.IGNORECASE,
        ),
    ),
    (
        "missing_property",
        re.compile(
            r"(Could not find property|missing property)\s+(?P<symbol>[\w:]+)",
            re.IGNORECASE,
        ),
    ),
    (
        "accessed_none",
        re.compile(r"Accessed None.*?(?:from node|property)?\s*(?P<symbol>[\w:]+)?", re.IGNORECASE),
    ),
)


@dataclass(frozen=True)
class BlueprintErrorInsight:
    line_number: int
    blueprint_name: str | None
    error_type: str
    message: str
    missing_symbol: str | None
    likely_stage: str
    possible_causes: tuple[str, ...]
    recommended_fixes: tuple[str, ...]
    verification_steps: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["possible_causes"] = list(self.possible_causes)
        data["recommended_fixes"] = list(self.recommended_fixes)
        data["verification_steps"] = list(self.verification_steps)
        return data


@dataclass(frozen=True)
class BlueprintAnalysisReport:
    project_root: Path
    log_path: Path
    total_errors: int
    insights: list[BlueprintErrorInsight] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_root": str(self.project_root),
            "log_path": str(self.log_path),
            "total_errors": self.total_errors,
            "insights": [insight.to_dict() for insight in self.insights],
        }


def analyze_blueprint_errors(
    project_root: str | Path,
    log_path: str | Path | None = None,
    read_limit_chars: int = DEFAULT_READ_LIMIT_CHARS,
) -> BlueprintAnalysisReport:
    """Analyze the latest or explicit UE log for Blueprint compile and runtime errors."""
    read_result = read_log_tail(project_root, log_path, read_limit_chars=read_limit_chars)
    insights: list[BlueprintErrorInsight] = []
    for line_number, line in enumerate(read_result.content.splitlines(), start=1):
        insight = _analyze_blueprint_line(line_number, line.strip())
        if insight is not None:
            insights.append(insight)

    return BlueprintAnalysisReport(
        project_root=read_result.info.project_root,
        log_path=read_result.info.log_path,
        total_errors=len(insights),
        insights=insights,
    )


def _analyze_blueprint_line(line_number: int, line: str) -> BlueprintErrorInsight | None:
    matches = [(name, pattern.search(line)) for name, pattern in BLUEPRINT_PATTERNS]
    matched = [(name, match) for name, match in matches if match is not None]
    if not matched:
        return None

    error_type = _select_error_type(matched)
    blueprint_name = _extract_blueprint_name(line, matched)
    missing_symbol = _extract_missing_symbol(matched)
    return BlueprintErrorInsight(
        line_number=line_number,
        blueprint_name=blueprint_name,
        error_type=error_type,
        message=line,
        missing_symbol=missing_symbol,
        likely_stage=_likely_stage(error_type),
        possible_causes=_possible_causes(error_type, missing_symbol),
        recommended_fixes=_recommended_fixes(error_type, missing_symbol),
        verification_steps=_verification_steps(error_type),
    )


def _select_error_type(matched: Sequence[tuple[str, re.Match[str]]]) -> str:
    matched_names = {name for name, _ in matched}
    for preferred in ("accessed_none", "compile_failed", "missing_function", "missing_property"):
        if preferred in matched_names:
            return preferred
    return matched[0][0]


def _extract_blueprint_name(
    line: str,
    matched: Sequence[tuple[str, re.Match[str]]],
) -> str | None:
    for _, match in matched:
        name = match.groupdict().get("name")
        if name:
            return name
    path_match = re.search(r"(/Game/[\w/.-]+|BP_[\w.-]+)", line)
    return path_match.group(1) if path_match else None


def _extract_missing_symbol(matched: Sequence[tuple[str, re.Match[str]]]) -> str | None:
    for _, match in matched:
        symbol = match.groupdict().get("symbol")
        if symbol:
            return symbol
    return None


def _likely_stage(error_type: str) -> str:
    if error_type == "runtime_error" or error_type == "accessed_none":
        return "Runtime/PIE"
    return "Blueprint Compile/Cook"


def _possible_causes(error_type: str, missing_symbol: str | None) -> tuple[str, ...]:
    if error_type == "accessed_none":
        return (
            "A Blueprint reference was not initialized before use.",
            "Runtime object creation or assignment order changed.",
        )
    if error_type in {"missing_function", "missing_property"} or missing_symbol:
        return (
            "A C++ function or property was renamed, removed, or no longer exposed to Blueprint.",
            "The Blueprint graph still contains stale generated bindings or broken pins.",
            "A plugin or module that defines the symbol failed to load.",
        )
    return (
        "The Blueprint graph contains invalid nodes, pins, or asset references.",
        "Cook exposed a Blueprint compile issue that was not fixed in editor.",
    )


def _recommended_fixes(error_type: str, missing_symbol: str | None) -> tuple[str, ...]:
    symbol_suffix = f" `{missing_symbol}`" if missing_symbol else ""
    if error_type == "accessed_none":
        return (
            "Add validity checks before using the referenced object.",
            "Trace where the variable should be assigned and fix initialization order.",
        )
    if error_type in {"missing_function", "missing_property"} or missing_symbol:
        return (
            f"Open the Blueprint and replace or refresh the missing symbol{symbol_suffix}.",
            "Refresh all nodes, compile, and save the Blueprint.",
            "If the symbol is C++, confirm it is still UFUNCTION/UPROPERTY Blueprint-visible.",
        )
    return (
        "Open the named Blueprint and compile it manually.",
        "Refresh broken nodes and fix disconnected pins.",
        "Resave dependent Blueprints and rerun Cook.",
    )


def _verification_steps(error_type: str) -> tuple[str, ...]:
    if error_type == "runtime_error" or error_type == "accessed_none":
        return (
            "Run the same PIE or runtime scenario and confirm the Blueprint runtime error is gone.",
        )
    return (
        "Compile the Blueprint in editor with no errors.",
        "Rerun Cook or packaging and confirm the Blueprint error is absent from the latest log.",
    )
