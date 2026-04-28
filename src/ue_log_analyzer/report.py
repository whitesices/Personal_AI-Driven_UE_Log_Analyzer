from __future__ import annotations

from collections import defaultdict

from .models import AnalysisResult, LogIssue


def render_markdown_report(result: AnalysisResult) -> str:
    info = result.log_info
    summary = result.summary
    lines: list[str] = [
        "# UE Log Analysis Report",
        "",
        "## Metadata",
        "",
        f"- Analyzed at: `{result.analyzed_at.isoformat()}`",
        f"- UE project: `{info.project_root}`",
        f"- Log file: `{info.log_path}`",
        f"- Log size: `{info.size_bytes}` bytes",
        f"- Characters analyzed: `{info.chars_read}` / limit `{info.read_limit_chars}`",
        f"- Tail truncated: `{'yes' if info.was_truncated else 'no'}`",
        "",
        "## Summary",
        "",
        f"- Total issues: `{summary.total_issues}`",
        f"- Blocking issue found: `{'yes' if summary.has_blocking_issue else 'no'}`",
        f"- Severity counts: `{summary.severity_counts}`",
        f"- Category counts: `{summary.category_counts}`",
        f"- Stage counts: `{summary.stage_counts}`",
        f"- Risk counts: `{summary.risk_counts}`",
        f"- Keyword counts: `{summary.keyword_counts}`",
        "",
        "## High Priority Issues",
        "",
    ]

    high_priority = [
        issue for issue in result.issues if issue.severity in {"critical", "high"}
    ]
    if high_priority:
        lines.extend(_render_issue_list(high_priority))
    else:
        lines.append("- No critical or high severity issues detected.")

    lines.extend(["", "## Issues By Category", ""])
    grouped: dict[str, list[LogIssue]] = defaultdict(list)
    for issue in result.issues:
        grouped[issue.category].append(issue)

    if grouped:
        for category in sorted(grouped):
            lines.extend([f"### {category}", ""])
            lines.extend(_render_issue_list(grouped[category]))
            lines.append("")
    else:
        lines.append("- No matching UE error or warning lines were detected.")

    lines.extend(["## Evidence Snippets", ""])
    if result.issues:
        for issue in result.issues[:20]:
            lines.extend(
                [
                    f"- Line `{issue.line_number}` [{issue.severity}/{issue.category}]",
                    f"  - Stage: `{issue.likely_stage}`",
                    f"  - Risk: `{issue.risk_level}`",
                    f"  - Keywords: `{', '.join(issue.matched_keywords)}`",
                    f"  - Text: `{_escape_inline(issue.message)}`",
                ]
            )
    else:
        lines.append("- No evidence snippets available.")

    lines.extend(["", "## Recommended Next Steps", ""])
    lines.extend(_recommended_next_steps(result))
    lines.append("")
    return "\n".join(lines)


def _render_issue_list(issues: list[LogIssue]) -> list[str]:
    rendered: list[str] = []
    for issue in issues:
        rendered.extend(
            [
                f"- Line `{issue.line_number}`: `{issue.severity}` / `{issue.category}`",
                f"  - Stage: `{issue.likely_stage}`",
                f"  - Risk: `{issue.risk_level}`",
                f"  - Matched: `{', '.join(issue.matched_keywords)}`",
                f"  - Message: `{_escape_inline(issue.message)}`",
                f"  - Interpretation: {issue.explanation}",
                f"  - Possible causes: {_format_inline_list(issue.possible_causes)}",
                f"  - Recommended fixes: {_format_inline_list(issue.recommended_fixes)}",
                f"  - Verification: {_format_inline_list(issue.verification_steps)}",
            ]
        )
    return rendered


def _recommended_next_steps(result: AnalysisResult) -> list[str]:
    categories = {issue.category for issue in result.issues}
    if not categories:
        return [
            "- 若 UE 仍然失败，请提高日志级别或检查更早的构建输出。",
            "- 确认分析的是最新一次失败对应的日志文件。",
        ]

    steps: list[str] = []
    if "cpp_compile_error" in categories:
        steps.append("- 从首个 C++ 编译错误开始修复，后续错误可能是连锁反应。")
    if "runtime_crash" in categories:
        steps.append("- 优先查看崩溃行附近调用栈和断言条件，结合最近 C++ 或 Blueprint 改动定位。")
    if "packaging_error" in categories:
        steps.append("- 查看 UAT/Cook 上下文，确认平台 SDK、资源 Cook 规则和插件打包配置。")
    if "plugin_compatibility" in categories:
        steps.append("- 核对插件支持的 UE 版本、模块加载配置和 `.uplugin` 依赖声明。")
    if "blueprint_error" in categories:
        steps.append("- 打开相关 Blueprint，重新编译并检查断开的节点、类型变化和资产引用。")
    if "asset_reference_error" in categories:
        steps.append("- 检查缺失资源路径、重定向器和软引用是否被 Cook 包含。")
    if "build_error" in categories:
        steps.append("- 检查 UnrealBuildTool 输出、目标平台配置和模块依赖。")
    steps.append("- 修复后重新运行相关构建或打包流程，并再次分析最新日志。")
    return steps


def _escape_inline(text: str) -> str:
    return text.replace("`", "'")


def _format_inline_list(values: tuple[str, ...]) -> str:
    if not values:
        return "`n/a`"
    return "; ".join(values)
