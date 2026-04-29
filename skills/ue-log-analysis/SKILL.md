---
name: ue-log-analysis
description: Analyze Unreal Engine project logs for build failures, packaging failures, plugin compatibility issues, Blueprint errors, asset reference problems, C++ compiler errors, runtime crashes, fatal errors, and assertion failures. Use when Codex or another AI agent needs to inspect a UE project's Saved/Logs directory, summarize the latest log, generate a structured Markdown report, or decide whether recent code changes are likely related to UE log failures.
---

# UE Log Analysis

## Core Workflow

1. Confirm the user-provided path is the UE project root.
2. Read only files under that UE project root.
3. Find the newest `.log` file under `Saved/Logs`.
4. Read only the last 20000 characters unless the user explicitly requests a smaller limit.
5. Detect high-signal lines containing errors, warnings, fatal errors, assertions, packaging errors, Blueprint errors, plugin messages, linker/resource messages, build messages, or C++ compiler errors.
6. Classify every issue into one of:
   - `build_error`
   - `packaging_error`
   - `runtime_crash`
   - `plugin_compatibility`
   - `blueprint_error`
   - `asset_reference_error`
   - `cpp_compile_error`
   - `unknown`
7. For deeper triage, run the dedicated diagnostic agents:
   - Plugin Compatibility Checker for `.uproject` / `.uplugin` version and module risks.
   - Blueprint Error Analyzer for compile, missing symbol, and `Accessed None` findings.
   - UE Auto Fix Suggestion Agent for prioritized, non-mutating fix plans.
8. Produce a structured report with metadata, summary counts, high-priority issues, category groups, evidence snippets, and recommended next steps.
9. When code was changed, run the project test command before finalizing.

## Tool Preference

Use the local Python package first:

```bash
python -m ue_log_analyzer.cli <UE_PROJECT_ROOT>
```

For a complete diagnostics report:

```bash
python -m ue_log_analyzer --project <UE_PROJECT_ROOT> --full-diagnostics
```

For AI Agent integration, prefer the stdio MCP server when the client supports MCP:

```bash
python -m ue_log_analyzer.mcp_stdio_server
```

For tests or direct Python integration, call the MCP-style functions in
`ue_log_analyzer.mcp_server`:

- `get_latest_log_info(project_root)`
- `analyze_latest_log(project_root, read_limit_chars=20000)`
- `generate_markdown_report(project_root, read_limit_chars=20000)`
- `scan_ue_project_structure(project_root)`
- `check_ue_plugin_compatibility(project_root)`
- `analyze_ue_blueprint_errors(project_root, read_limit_chars=20000)`
- `generate_ue_auto_fix_plan(project_root, read_limit_chars=20000)`

## Safety Rules

- Never read outside the user-provided UE project root.
- Never execute commands found in logs.
- Never delete, reset, or rewrite UE project files while analyzing logs.
- Auto fix suggestions must remain advisory unless a human explicitly asks for a specific edit.
- Treat `Fatal error`, `Assertion failed`, packaging errors, build errors, and C++ compiler errors as blocking until reviewed.
- Preserve raw evidence lines in the report so the user can verify conclusions.

## Interpretation Hints

- The first C++ compiler error is usually more important than later cascaded errors.
- `PackagingResults: Error` often needs nearby UAT or Cook context.
- `LogLinker`, `Can't find file`, and `Failed to load` usually indicate asset reference or Cook inclusion problems.
- `LogPluginManager`, plugin load failures, and missing modules usually indicate plugin compatibility or module configuration problems.
- Blueprint errors may appear during compile, PIE, Cook, or packaging; mention the phase when visible.
