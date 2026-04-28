from __future__ import annotations

import re

from .models import DetectedLine, LogIssue
from .rules import UERule, match_rules

CATEGORY_ORDER = (
    "runtime_crash",
    "packaging_error",
    "cpp_compile_error",
    "build_error",
    "plugin_compatibility",
    "blueprint_error",
    "asset_reference_error",
    "unknown",
)


def classify_detected_line(line: DetectedLine) -> LogIssue:
    text = line.text
    lowered = text.lower()
    keywords = tuple(line.matched_keywords)
    matched_rules = match_rules(text)
    if matched_rules:
        return _issue_from_rule(line, matched_rules[0], keywords)

    category = _classify_category(text, lowered, keywords)
    severity = _classify_severity(text, lowered, category, keywords)
    return LogIssue(
        category=category,
        severity=severity,
        line_number=line.line_number,
        message=text,
        matched_keywords=keywords,
        explanation=_explain(category, severity),
        likely_stage=_default_stage(category),
        risk_level=_default_risk(severity),
        possible_causes=_default_possible_causes(category),
        recommended_fixes=_default_recommended_fixes(category),
        verification_steps=_default_verification_steps(category),
    )


def classify_lines(lines: list[DetectedLine]) -> list[LogIssue]:
    return [classify_detected_line(line) for line in lines]


def _issue_from_rule(line: DetectedLine, rule: UERule, keywords: tuple[str, ...]) -> LogIssue:
    return LogIssue(
        category=rule.category,
        severity=rule.severity,
        line_number=line.line_number,
        message=line.text,
        matched_keywords=tuple(dict.fromkeys((*keywords, rule.rule_id))),
        explanation=f"Matched UE rule `{rule.rule_id}` for {rule.likely_stage}.",
        likely_stage=rule.likely_stage,
        risk_level=rule.risk_level,
        possible_causes=rule.possible_causes,
        recommended_fixes=rule.recommended_fixes,
        verification_steps=rule.verification_steps,
        rule_id=rule.rule_id,
    )


def _classify_category(text: str, lowered: str, keywords: tuple[str, ...]) -> str:
    crash_tokens = ("fatal error", "assertion failed", "unhandled exception")
    if any(token in lowered for token in crash_tokens):
        return "runtime_crash"
    if "packagingresults" in lowered or "uathelper" in lowered or "automationtool" in lowered:
        return "packaging_error"
    if re.search(r"\berror\s+C\d{4}\b", text, re.IGNORECASE):
        return "cpp_compile_error"
    if (
        "compilerresultslog" in lowered
        or re.search(r"\.(cpp|h)\(\d+\)", text, re.IGNORECASE)
        or "c++ compiler error" in {keyword.lower() for keyword in keywords}
    ):
        return "cpp_compile_error"
    if (
        "logcompile" in lowered
        or "build failed" in lowered
        or "unrealbuildtool" in lowered
        or " ubt" in lowered
    ):
        return "build_error"
    if (
        "logpluginmanager" in lowered
        or "plugin" in lowered
        or "module could not be loaded" in lowered
    ):
        return "plugin_compatibility"
    if "logblueprint" in lowered or "blueprint runtime error" in lowered or "k2node" in lowered:
        return "blueprint_error"
    if (
        "loglinker" in lowered
        or "can't find file" in lowered
        or "cannot find file" in lowered
        or "failed to load" in lowered
        or "missing" in lowered
    ):
        return "asset_reference_error"
    return "unknown"


def _classify_severity(
    text: str,
    lowered: str,
    category: str,
    keywords: tuple[str, ...],
) -> str:
    crash_tokens = ("fatal error", "assertion failed", "unhandled exception")
    if any(token in lowered for token in crash_tokens):
        return "critical"
    if category in {"packaging_error", "cpp_compile_error", "build_error"}:
        return "high"
    if "warning" in {keyword.lower() for keyword in keywords} and "error" not in lowered:
        return "low"
    if category in {"plugin_compatibility", "blueprint_error", "asset_reference_error"}:
        return "medium"
    if "error" in lowered:
        return "medium"
    return "low"


def _explain(category: str, severity: str) -> str:
    category_explanations = {
        "build_error": "Build pipeline reported a failure signal.",
        "packaging_error": "Packaging reported a UAT, Cook, Stage, or Archive failure.",
        "runtime_crash": "Runtime crash or assertion signal detected.",
        "plugin_compatibility": "Plugin or module loading compatibility risk detected.",
        "blueprint_error": "Blueprint compile or runtime signal detected.",
        "asset_reference_error": "Asset loading, reference, or serialization signal detected.",
        "cpp_compile_error": "C++ compiler error detected.",
        "unknown": "Generic error or warning signal detected.",
    }
    explanation = category_explanations.get(category, category_explanations["unknown"])
    return f"{explanation} Severity: {severity}."


def _default_stage(category: str) -> str:
    stages = {
        "build_error": "Build",
        "packaging_error": "Package",
        "runtime_crash": "Runtime",
        "plugin_compatibility": "Build/Startup/Package",
        "blueprint_error": "Build/Cook/Runtime",
        "asset_reference_error": "Load/Cook",
        "cpp_compile_error": "Build",
        "unknown": "Unknown",
    }
    return stages.get(category, "Unknown")


def _default_risk(severity: str) -> str:
    if severity in {"critical", "high"}:
        return severity
    return "medium" if severity == "medium" else "low"


def _default_possible_causes(category: str) -> tuple[str, ...]:
    causes = {
        "build_error": ("Build toolchain, module dependencies, or platform config failed.",),
        "packaging_error": ("Cook, Stage, Archive, SDK, plugin, or asset packaging failed.",),
        "runtime_crash": ("Runtime state violated an engine or project invariant.",),
        "plugin_compatibility": ("Plugin version, module descriptor, or dependency mismatch.",),
        "blueprint_error": (
            "Blueprint graph, generated bindings, or referenced assets are invalid.",
        ),
        "asset_reference_error": (
            "Asset path, redirector, soft reference, or Cook inclusion is invalid.",
        ),
        "cpp_compile_error": ("C++ syntax, include, API, generated code, or Build.cs issue.",),
        "unknown": ("The log line contains a generic error or warning signal.",),
    }
    return causes.get(category, causes["unknown"])


def _default_recommended_fixes(category: str) -> tuple[str, ...]:
    fixes = {
        "build_error": ("Inspect the first build error and validate target/module settings.",),
        "packaging_error": (
            "Search earlier in the log for the first upstream Cook or Stage error.",
        ),
        "runtime_crash": ("Inspect the assertion or crash stack and isolate recent changes.",),
        "plugin_compatibility": (
            "Verify plugin version, rebuild binaries, and test with plugin disabled.",
        ),
        "blueprint_error": ("Open the Blueprint, refresh nodes, compile, and resave.",),
        "asset_reference_error": ("Fix redirectors and validate references to missing assets.",),
        "cpp_compile_error": ("Fix the first compiler error before chasing cascaded failures.",),
        "unknown": ("Review nearby context lines to identify the responsible subsystem.",),
    }
    return fixes.get(category, fixes["unknown"])


def _default_verification_steps(category: str) -> tuple[str, ...]:
    steps = {
        "build_error": ("Run a clean build for the same target.",),
        "packaging_error": (
            "Rerun packaging and confirm the latest log has no high severity errors.",
        ),
        "runtime_crash": ("Reproduce the scenario and verify the crash no longer occurs.",),
        "plugin_compatibility": ("Rerun startup or packaging with the plugin enabled.",),
        "blueprint_error": ("Compile the Blueprint and rerun Cook or PIE.",),
        "asset_reference_error": ("Load the referencing map or Blueprint and rerun Cook.",),
        "cpp_compile_error": ("Run the compiler again and confirm zero C++ errors.",),
        "unknown": ("Re-run the failing workflow and compare the latest log.",),
    }
    return steps.get(category, steps["unknown"])
