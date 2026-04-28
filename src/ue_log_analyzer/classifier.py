from __future__ import annotations

import re

from .models import DetectedLine, LogIssue

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
    category = _classify_category(text, lowered, keywords)
    severity = _classify_severity(text, lowered, category, keywords)
    return LogIssue(
        category=category,
        severity=severity,
        line_number=line.line_number,
        message=text,
        matched_keywords=keywords,
        explanation=_explain(category, severity),
    )


def classify_lines(lines: list[DetectedLine]) -> list[LogIssue]:
    return [classify_detected_line(line) for line in lines]


def _classify_category(text: str, lowered: str, keywords: tuple[str, ...]) -> str:
    if any(token in lowered for token in ("fatal error", "assertion failed", "unhandled exception")):
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
    if "logcompile" in lowered or "build failed" in lowered or "unrealbuildtool" in lowered or " ubt" in lowered:
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
    if any(token in lowered for token in ("fatal error", "assertion failed", "unhandled exception")):
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
        "build_error": "构建链路出现失败信号，优先检查 UnrealBuildTool、编译配置和依赖模块。",
        "packaging_error": "打包阶段出现错误，通常需要检查 UAT、Cook、资源和平台配置日志上下文。",
        "runtime_crash": "运行时出现崩溃或断言失败，需要优先定位调用栈、断言条件和最近代码改动。",
        "plugin_compatibility": "插件或模块加载存在兼容风险，建议核对插件版本、启用状态和目标 UE 版本。",
        "blueprint_error": "蓝图编译或运行时信号异常，建议打开对应 Blueprint 查看节点和引用。",
        "asset_reference_error": "资源加载或引用缺失，建议检查路径、重定向器和 Cook 资源包含规则。",
        "cpp_compile_error": "C++ 编译器报告错误，建议从首个编译错误行开始修复。",
        "unknown": "日志行包含通用错误或警告信号，需要结合上下文继续判断。",
    }
    return f"{category_explanations.get(category, category_explanations['unknown'])} 严重度：{severity}。"

