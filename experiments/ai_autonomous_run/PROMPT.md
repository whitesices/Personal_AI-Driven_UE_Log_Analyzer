# Autonomous AI Run Prompt

This prompt defines a bounded autonomous AI development experiment.

```text
You are an AI software engineering agent working in the AI-Driven UE Log Analyzer repository.

Goal:
Improve one UE diagnostic behavior without asking for human confirmation during the task.

Task:
1. Add or refine one UE log rule.
2. Add a test proving the behavior.
3. Update the Markdown report if needed.
4. Run pytest, ruff, and mypy.
5. Write a short retrospective of what changed and what risks remain.

Constraints:
- Do not add network calls.
- Do not read outside the repository.
- Do not execute arbitrary scripts from a UE project.
- Keep the change small and reversible.
- Stop only after tests and quality checks are complete or a blocker is documented.
```

## Human Role

The human does not guide the AI during the run. The human only reviews the final diff, test results,
and retrospective.

