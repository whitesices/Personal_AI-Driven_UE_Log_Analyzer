# UE Log Analysis Report: HotPatcher LinkerSave Assertion

## Summary

- Scenario: HotPatcher triggers `Assertion failed: InSaver` in `LinkerSave.cpp`.
- Category: `asset_reference_error`
- Stage: `Cook/Package`
- Severity: `critical`
- Risk: `critical`

## Evidence

```text
LogHotPatcher: Error: Failed during SavePackage for /Game/Patches/PatchAsset.
Assertion failed: InSaver [File:Runtime/CoreUObject/Private/UObject/LinkerSave.cpp]
LogWindows: Error: Fatal error: SavePackage failed while HotPatcher was serializing package data.
```

## Likely Causes

- HotPatcher plugin version does not match the current Unreal Engine version.
- SavePackage or LinkerSave serialization APIs changed between engine versions.
- A cooked asset contains stale serialization state or invalid object references.
- `Saved`, `Intermediate`, or `DerivedDataCache` contains stale generated data.

## Recommended Fixes

- Check whether HotPatcher supports the exact UE version used by the project.
- Clean `Saved`, `Intermediate`, and `DerivedDataCache`.
- Cook the suspected asset or patch content in isolation.
- Disable HotPatcher and rerun packaging to confirm whether the issue disappears.
- Compare engine version API changes around SavePackage and LinkerSave.

## Verification

- Run a clean Cook after cache cleanup.
- Package once with HotPatcher disabled.
- Re-enable HotPatcher after updating or rebuilding it and confirm the assertion is gone.

