# Advanced Diagnostic Agents

This document describes the third-layer diagnostic capabilities added on top of
the original UE log analyzer.

## 1. Goal

The first version focused on reading the latest UE log and classifying high-signal
error lines. The strengthened version adds three focused, read-only diagnostic
agents:

- UE Plugin Compatibility Checker
- UE Blueprint Error Analyzer
- UE Auto Fix Suggestion Agent

These agents make the project more useful for real UE workflows and more valuable
as an AI Agent engineering interview demo.

## 2. UE Plugin Compatibility Checker

Module:

```text
src/ue_log_analyzer/plugin_checker.py
```

Public API:

```python
check_plugin_compatibility(project_root)
```

It inspects project-local `.uproject` and `.uplugin` descriptors and reports:

- plugin `EngineVersion` vs project `EngineAssociation` mismatch
- invalid `Modules` schema
- plugin module declared without Source or Binaries artifacts
- enabled project plugin not present under `Plugins/`

Safety boundary:

- It reads only descriptor files and file presence under the UE project root.
- It does not load plugin code.
- It does not run UnrealBuildTool, Unreal Editor, or project scripts.

## 3. UE Blueprint Error Analyzer

Module:

```text
src/ue_log_analyzer/blueprint_analyzer.py
```

Public API:

```python
analyze_blueprint_errors(project_root, log_path=None, read_limit_chars=20000)
```

It extracts Blueprint-specific findings from the bounded log tail, including:

- `LogBlueprint: Error`
- `Compile of BP_* failed`
- `Blueprint Runtime Error`
- `Accessed None`
- missing Blueprint-visible function/property symbols
- K2 node warnings

Each insight includes:

- line number
- Blueprint name when visible
- error type
- missing symbol when visible
- likely UE stage
- possible causes
- recommended fixes
- verification steps

## 4. UE Auto Fix Suggestion Agent

Module:

```text
src/ue_log_analyzer/auto_fix_agent.py
```

Public API:

```python
generate_auto_fix_plan(project_root, log_path=None, read_limit_chars=20000)
```

It combines:

- core log rule matches
- plugin compatibility findings
- Blueprint error insights

Then it returns a prioritized fix plan with:

- priority
- category
- risk level
- rationale
- actions
- verification steps
- safety notes

Important: this is not an auto-modifying repair bot. It is a controlled AI Agent
pattern: gather context, propose fixes, and keep the human in control of risky UE
project changes.

## 5. CLI Usage

```bash
python -m ue_log_analyzer --project "D:/UEProjects/MyProject" --plugin-check
python -m ue_log_analyzer --project "D:/UEProjects/MyProject" --blueprint-analysis
python -m ue_log_analyzer --project "D:/UEProjects/MyProject" --fix-plan
python -m ue_log_analyzer --project "D:/UEProjects/MyProject" --full-diagnostics
```

All output paths remain constrained to the UE project directory when `--output` is used.

## 6. MCP Tools

The stdio MCP server also exposes:

- `check_ue_plugin_compatibility`
- `analyze_ue_blueprint_errors`
- `generate_ue_auto_fix_plan`

This lets Claude Desktop, Claude Code, Cursor, or another MCP-capable AI client request
structured UE diagnostics without gaining arbitrary filesystem or command execution access.

## 7. Interview Talking Points

- Skill captures the workflow and UE triage heuristics.
- MCP exposes safe context to AI clients.
- Hooks keep AI-generated changes inside a verification loop.
- Diagnostic agents show the shift from keyword parsing to domain-specific reasoning.
- Tests prove these agents work on plugin, Blueprint, CLI, and MCP paths.
