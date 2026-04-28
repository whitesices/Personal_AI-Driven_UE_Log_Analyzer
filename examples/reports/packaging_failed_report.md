# UE Log Analysis Report: Packaging Failed

## Summary

- Scenario: AutomationTool and PackagingResults report an unknown Cook failure.
- Category: `packaging_error`
- Stage: `Cook/Package`
- Severity: `high`
- Risk: `high`

## Evidence

```text
UATHelper: Packaging (Windows): AutomationTool Error: Cook failed.
LogCook: Error: Unknown Cook Failure
PackagingResults: Error: Unknown Cook Failure
AutomationTool exiting with ExitCode=25 (Error_UnknownCookFailure)
```

## Likely Causes

- A specific Cook error occurred earlier and was summarized as Unknown Cook Failure.
- A bad asset, Blueprint compile issue, plugin error, or platform configuration issue broke Cook.
- AutomationTool failed after an upstream Cook problem.

## Recommended Fixes

- Search earlier in the log for the first high-signal `Error`.
- Fix asset, Blueprint, plugin, or SDK errors before the PackagingResults summary line.
- Clear DerivedDataCache and rerun Cook with verbose logging.

## Verification

- Rerun packaging after fixing the earliest upstream error.
- Confirm AutomationTool exits with code 0.
- Confirm the latest log has no `PackagingResults: Error` lines.

