# Retrospective

## 1. What Went Well

- The project evolved from a simple log analyzer into an AI Agent engineering showcase.
- Core logic stayed modular: reader, detector, rules, classifier, analyzer, report, CLI, MCP.
- MCP moved from MCP-style functions to a real stdio server adapter.
- UE-specific rules now include stages, causes, fixes, verification steps, and risk levels.
- Tests cover both business logic and integration boundaries.
- Docs now explain product thinking, engineering decisions, and interview value.

## 2. Limits Of AI-Generated Content

- The first implementation leaned on keyword classification and needed a stronger UE-specific rule model.
- The first MCP layer was useful but not a true stdio MCP server.
- Initial CLI output allowed writing outside the UE project directory.
- Test infrastructure needed adjustment for the local Windows sandbox.
- Human review is still required for production UE plugin and engine-version edge cases.

## 3. Human Reviewer Intervention Points

A reviewer should inspect:

- Path security for all file reads and writes.
- MCP server startup and tool registration.
- UE rules for real-world accuracy.
- Whether sample logs avoid sensitive project data.
- Whether CI and local quality commands match.

## 4. Next Optimization Directions

1. Add a configurable YAML rule pack.
2. Add a full stdio MCP integration smoke test when MCP SDK is available.
3. Add HTML or SARIF report output.
4. Add Git Hook installation helper.
5. Add multi-log trend analysis across build attempts.
6. Add deeper UE AutomationTool and Cook phase parsing.

## 5. Interview Narrative

Suggested pitch:

```text
This is not just a log parser. I used AI as the primary development agent to build a
small but complete engineering system around Unreal Engine diagnostics. The project
shows how Skill captures domain workflow, MCP exposes safe project context to AI,
Hooks close the validation loop, Tests and CI keep the result reliable, and Docs plus
Retrospective preserve the development process.
```

Key points to emphasize:

- UE domain depth: LinkerSave, SavePackage, Cook, UAT, Blueprint, SDK, Pak/IoStore.
- AI engineering: MCP stdio server, Skill, Hook, CI.
- Safety: path-bounded reads and writes, no external API calls, no arbitrary script execution.
- Reliability: pytest, ruff, mypy, GitHub Actions.

## 6. Skill / MCP / Hook Value

- Skill turns repeated UE log triage experience into reusable AI procedure.
- MCP lets AI access UE project context through controlled tools rather than raw filesystem access.
- Hook connects AI code changes to automatic verification.
- Tests and CI make the Agent workflow auditable.
- Docs and retrospective make the AI-led process explainable in an interview.

