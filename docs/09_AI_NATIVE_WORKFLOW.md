# AI Native Workflow

This document explains the development method behind this project. It is written for interview review,
not as marketing copy.

## 1. Core Idea

The project uses AI as the primary engineering agent, but keeps verification explicit.

```text
User goal
  -> AI task decomposition
  -> AI implementation
  -> automated tests and quality gates
  -> human review of risk boundaries
  -> docs and retrospective
```

The key point is not "AI wrote code". The key point is that the repository contains the workflow
surrounding AI-generated code: Skill, MCP, Hook, tests, CI, docs, examples, and retrospectives.

## 2. Working Method

### Step 1: Give AI a product-level target

The prompt describes a UE developer pain point, not only a coding task:

- Build failures.
- Packaging failures.
- Blueprint errors.
- C++ compile errors.
- Assertion failures.
- Plugin compatibility.

### Step 2: Ask AI to decompose the system

The AI decomposes the project into:

- Reader: safe project-bounded log reading.
- Detector: UE signal detection.
- Rules: UE-specific diagnosis rules.
- Classifier: category, severity, stage, and risk mapping.
- Reporter: structured Markdown output.
- MCP: AI access to UE project context.
- Skill: repeatable log triage workflow.
- Hook: automatic verification points.
- Tests and CI: reliability gates.

### Step 3: Let AI implement, but require evidence

The implementation is accepted only after:

- `python -m pytest`
- `ruff check .`
- `mypy src`
- `python -m build`

This prevents the project from becoming a folder of plausible but unverified generated files.

### Step 4: Human review focuses on boundaries

Human review is most valuable on:

- File-system safety.
- Whether MCP is real or only described.
- Whether UE rules are too broad.
- Whether reports are actionable.
- Whether docs match the actual code.

## 3. Use, Understand, Create

The feedback from the first interview round emphasized three levels:

| Level | Meaning | Project Evidence |
| --- | --- | --- |
| Use | Can operate Claude Code / Cursor / MCP-style tools | README usage and CLI/MCP commands |
| Understand | Can explain why Skill, MCP, and Hook exist | docs, Skill design, MCP design, Hook design |
| Create | Can build custom Skill, MCP server, and Hook | `skills/`, `mcp_stdio_server.py`, `hooks/` |

## 4. Skill / MCP / Hook Roles

### Skill

Skill captures the domain workflow:

- Which UE logs to inspect.
- Which signals matter.
- How to reason about Build / Cook / Stage / Package / Runtime.
- How to produce fixes and verification steps.

### MCP

MCP is the safe bridge between AI and local project context:

- The AI does not read arbitrary files.
- The MCP tools expose controlled project context.
- The tools return structured results that an Agent can reason about.

### Hook

Hook closes the validation loop:

- After AI code changes: run tests.
- Before commit: scan latest UE logs for blocking issues.

## 5. Human-in-the-loop vs Autonomous AI

This repository distinguishes two modes:

### AI-led with human review

This is the main project mode.

The AI writes most implementation and docs, while the human defines the goal and reviews outputs.
This is realistic for production work.

### Autonomous AI experiment

The experiment under `experiments/ai_autonomous_run/` records a smaller run where AI is expected to
complete a bounded change without mid-task human confirmation. The human only validates at the end.

This avoids overstating the project as "fully autonomous" while still showing that autonomous
development was tested in a controlled scope.

## 6. Interview Narrative

Suggested summary:

```text
I used this project to practice AI-native engineering, not just AI-assisted coding.
The Skill encodes UE log triage knowledge, MCP gives AI a safe tool interface to the project,
Hooks add automatic verification, and tests/CI keep the output reliable. The docs capture not only
what was built, but how AI decomposed the work and where human review still matters.
```

