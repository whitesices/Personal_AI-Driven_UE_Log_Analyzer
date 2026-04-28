# Generated Output

This experiment record is intentionally small. It documents the kind of output expected from a
fully autonomous AI run.

## Candidate Autonomous Change

Refine an overly broad UE diagnostic rule:

- Before: a log line containing only `HotPatcher` or `SavePackage` could match the critical
  LinkerSave / InSaver rule.
- After: the critical rule should require a stronger signal such as `Assertion failed: InSaver` or
  `LinkerSave.cpp`.

## Expected Code Areas

- `src/ue_log_analyzer/rules.py`
- `tests/test_rules.py`
- `src/ue_log_analyzer/report.py` if report output needs to surface the improved diagnosis.

## Expected Validation

```bash
python -m pytest
ruff check .
mypy src
```

