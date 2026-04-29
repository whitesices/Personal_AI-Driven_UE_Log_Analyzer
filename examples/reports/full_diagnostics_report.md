# UE Full Diagnostics Report

This synthetic example shows the combined output style enabled by:

```bash
python -m ue_log_analyzer --project examples/sample_ue_project --full-diagnostics
```

## Core Log Analysis

- Category: `runtime_crash`
- Severity: `critical`
- Stage: `Cook/Package`
- Risk: `blocking`
- Evidence: `Assertion failed: InSaver [File:Runtime/CoreUObject/Private/UObject/LinkerSave.cpp]`
- Possible causes:
  - SavePackage failed while serializing an asset.
  - A plugin may be using an API path that changed between UE versions.
  - A cooked asset may contain stale serialized references.
- Recommended fixes:
  - Check whether the plugin version matches the UE engine version.
  - Clean `Saved`, `Intermediate`, and `DerivedDataCache`.
  - Cook the suspected asset separately.
  - Disable the suspected plugin and rerun packaging to isolate the failure.

## UE Plugin Compatibility Report

- Engine association: `5.3`
- Plugins scanned: `1`
- Issues found: `2`

### Issues

- `high` / `engine_version_mismatch`: HotPatcher
  - Evidence: `project=5.3, plugin=5.1`
  - Recommended fix: install or rebuild a HotPatcher version targeting UE 5.3.
  - Verification: restart the editor and confirm no plugin manager errors remain.

- `high` / `module_missing`: HotPatcherRuntime
  - Evidence: `Plugins/HotPatcher/HotPatcher.uplugin`
  - Recommended fix: restore source or prebuilt binaries for the declared module.
  - Verification: rebuild the project target that loads the plugin.

## UE Blueprint Error Analysis

- Blueprint findings: `1`

### Findings

- Line `42`: `compile_failed`
  - Blueprint: `BP_Player`
  - Missing symbol: `GiveDamage`
  - Stage: `Blueprint Compile/Cook`
  - Possible cause: a C++ BlueprintCallable function was renamed or removed.
  - Recommended fix: refresh nodes, replace the missing symbol, compile, and save.
  - Verification: rerun packaging and confirm the Blueprint error is absent.

## UE Auto Fix Suggestion Plan

### Suggested Actions

- P10: Address runtime_crash from latest UE log
  - Action: inspect the SavePackage assertion and isolate the asset/plugin context.
  - Verify: rerun Cook or packaging and analyze the newest log.
  - Safety: advisory only; no project files are modified.

- P20: Fix plugin compatibility issue: HotPatcher
  - Action: align the plugin version with the project engine version.
  - Verify: confirm no `LogPluginManager` or module load failure remains.
  - Safety: advisory only; no project files are modified.

- P30: Repair Blueprint issue: BP_Player
  - Action: refresh missing function nodes and recompile the Blueprint.
  - Verify: compile in editor and rerun Cook.
  - Safety: advisory only; no project files are modified.
