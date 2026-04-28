# Personal_AI-Driven_UE_Log_Analyzer

[![CI](https://github.com/whitesices/Personal_AI-Driven_UE_Log_Analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/whitesices/Personal_AI-Driven_UE_Log_Analyzer/actions/workflows/ci.yml)

AI-Driven UE Log Analyzer is a local, safety-bounded Unreal Engine log analysis toolkit built as an interview-ready AI Agent engineering showcase.

It demonstrates a full loop:

```text
UE Project Saved/Logs
        |
        v
Python Analyzer + UE Rule Library
        |
        +--> CLI Markdown Report
        +--> MCP stdio Server for AI Agents
        +--> Skill-guided UE triage workflow
        +--> Hooks for test and pre-commit checks
        +--> Tests / CI / Docs / Retrospective
```

## Why This Shows AI-led Development

This project is not only a log parser. It is designed to show how AI can lead a small but complete engineering workflow:

- **Skill** captures repeatable UE log analysis expertise.
- **MCP** exposes safe UE project context to AI tools.
- **Hook** closes the loop after AI code changes and before Git commits.
- **Tests / CI** keep behavior reliable.
- **Docs / Retrospective** preserve the AI-led development process for review.

## Features

- Find the newest `.log` file under `<UE_PROJECT>/Saved/Logs`.
- Read only inside the user-provided UE project directory.
- Analyze only the trailing log content by default.
- Detect UE-specific issues, including LinkerSave, SavePackage, Assertion failed, AutomationTool, PackagingResults, Unknown Cook Failure, Blueprint compile errors, missing assets, plugin/module failures, C++ compile errors, Shader/DDC, SDK, Pak, and IoStore issues.
- Generate structured Markdown reports with:
  - category
  - severity
  - likely UE stage
  - risk level
  - possible causes
  - recommended fixes
  - verification steps
- Run as CLI, MCP stdio server, or Python API.
- Provide hooks, tests, CI, Skill docs, and interview artifacts.

## Install

```bash
python -m pip install -e ".[dev]"
```

## CLI Usage

Preferred explicit form:

```bash
python -m ue_log_analyzer --project "D:/UEProjects/MyProject"
```

Save a report inside the UE project:

```bash
python -m ue_log_analyzer --project "D:/UEProjects/MyProject" --output "AIReports/latest_report.md"
```

Backward-compatible console script:

```bash
ue-log-analyzer "D:/UEProjects/MyProject"
```

Analyze a specific project-local log:

```bash
python -m ue_log_analyzer --project "D:/UEProjects/MyProject" --log-path "Saved/Logs/MyProject.log"
```

Security note: `--output` and `--log-path` are constrained to the UE project directory.

## MCP Server Usage

Run the real stdio MCP server:

```bash
python -m ue_log_analyzer.mcp_stdio_server
```

Example MCP client configuration for Claude Desktop / Claude Code / Cursor:

```json
{
  "mcpServers": {
    "ue-log-analyzer": {
      "command": "python",
      "args": ["-m", "ue_log_analyzer.mcp_stdio_server"]
    }
  }
}
```

This is a configuration template. The project provides a real stdio server adapter, but each client may require environment-specific setup.

Registered tools:

- `get_latest_log_info`
- `analyze_latest_log`
- `generate_markdown_report`
- `scan_ue_project_structure`

See [MCP stdio server design](docs/08_MCP_STDIO_SERVER.md).

## Hook Usage

Run tests after AI code changes:

```bash
python hooks/after_code_change.py
```

Scan latest UE log before commit:

```bash
python hooks/pre_commit_scan.py "D:/UEProjects/MyProject"
```

The pre-commit scan returns non-zero when critical or high severity UE log issues are found.

## Skill Usage

The UE Log Analysis Skill lives at:

```text
skills/ue-log-analysis/SKILL.md
```

The Skill defines the repeatable AI workflow for:

- selecting the latest log
- enforcing safe project-bound reads
- identifying UE build/cook/package/runtime stages
- explaining likely causes
- recommending fixes
- validating after code changes

## Tests And Quality

```bash
python -m pytest
ruff check .
mypy src
python -m build
```

GitHub Actions CI runs:

- install
- pytest
- ruff
- mypy

## Example Reports

- [HotPatcher LinkerSave Assertion](examples/reports/hotpatcher_linkersave_assertion_report.md)
- [Packaging Failed](examples/reports/packaging_failed_report.md)
- [Blueprint Compile Error](examples/reports/blueprint_compile_error_report.md)

Sample logs are under:

```text
examples/sample_ue_project/Saved/Logs/
```

## Safety Boundaries

- No external API calls.
- No log upload.
- No Unreal Editor launch.
- No execution of scripts from UE projects.
- Input log paths must stay inside the UE project directory.
- CLI output paths must stay inside the UE project directory.
- MCP tools reuse the same safety-bounded business functions.
- Long logs are read through bounded tail analysis.

## Documentation Map

- [Original Prompt](docs/00_ORIGINAL_PROMPT.md)
- [Agent Task Breakdown](docs/01_AGENT_TASK_BREAKDOWN.md)
- [AI Development Log](docs/02_AI_DEVELOPMENT_LOG.md)
- [Human Review Notes](docs/03_HUMAN_REVIEW_NOTES.md)
- [PRD](docs/PRD.md)
- [Usage Guide](docs/USAGE_GUIDE.md)
- [Project Memory](docs/PROJECT_MEMORY.md)
- [Technical Design](docs/TECHNICAL_DESIGN.md)
- [AI Workflow](docs/AI_WORKFLOW.md)
- [MCP Design](docs/MCP_DESIGN.md)
- [MCP stdio Server](docs/08_MCP_STDIO_SERVER.md)
- [Skill Design](docs/SKILL_DESIGN.md)
- [Hook Design](docs/HOOK_DESIGN.md)
- [Test Report](docs/06_TEST_REPORT.md)
- [Retrospective](docs/07_RETROSPECTIVE.md)

## Roadmap

- Add configurable YAML UE rule packs.
- Add stdio MCP integration smoke tests.
- Add HTML and SARIF report output.
- Add Git Hook installation helper.
- Add multi-log trend analysis across repeated build attempts.
- Add deeper AutomationTool and Cook phase parsers.

