from __future__ import annotations

import re

from .models import DetectedLine

KEYWORD_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("Fatal error", re.compile(r"\bFatal error\b", re.IGNORECASE)),
    ("Assertion failed", re.compile(r"\bAssertion failed\b", re.IGNORECASE)),
    ("PackagingResults: Error", re.compile(r"PackagingResults:\s*Error", re.IGNORECASE)),
    ("Unhandled Exception", re.compile(r"\bUnhandled Exception\b", re.IGNORECASE)),
    ("C++ compiler error", re.compile(r"\berror\s+C\d{4}\b", re.IGNORECASE)),
    ("Blueprint Runtime Error", re.compile(r"Blueprint Runtime Error", re.IGNORECASE)),
    ("LogBlueprint", re.compile(r"\bLogBlueprint\b", re.IGNORECASE)),
    ("LogPluginManager", re.compile(r"\bLogPluginManager\b", re.IGNORECASE)),
    ("LogLinker", re.compile(r"\bLogLinker\b", re.IGNORECASE)),
    ("LogCompile", re.compile(r"\bLogCompile\b", re.IGNORECASE)),
    ("CompilerResultsLog", re.compile(r"\bCompilerResultsLog\b", re.IGNORECASE)),
    ("Failed to load", re.compile(r"\bFailed to load\b", re.IGNORECASE)),
    ("Can't find file", re.compile(r"Can(?:not|'t)\s+find\s+file", re.IGNORECASE)),
    ("Build failed", re.compile(r"\bBuild failed\b", re.IGNORECASE)),
    ("Error", re.compile(r"\bError\b", re.IGNORECASE)),
    ("Warning", re.compile(r"\bWarning\b", re.IGNORECASE)),
)


def detect_issue_lines(log_text: str) -> list[DetectedLine]:
    detected: list[DetectedLine] = []
    for index, line in enumerate(log_text.splitlines(), start=1):
        matches = tuple(
            keyword for keyword, pattern in KEYWORD_PATTERNS if pattern.search(line)
        )
        if matches:
            detected.append(
                DetectedLine(
                    line_number=index,
                    text=line.strip(),
                    matched_keywords=matches,
                )
            )
    return detected

