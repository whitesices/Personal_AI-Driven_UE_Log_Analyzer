from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class UERule:
    rule_id: str
    pattern: str
    category: str
    severity: str
    likely_stage: str
    risk_level: str
    possible_causes: tuple[str, ...]
    recommended_fixes: tuple[str, ...]
    verification_steps: tuple[str, ...]

    def matches(self, text: str) -> bool:
        return re.search(self.pattern, text, re.IGNORECASE) is not None

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "pattern": self.pattern,
            "category": self.category,
            "severity": self.severity,
            "likely_stage": self.likely_stage,
            "risk_level": self.risk_level,
            "possible_causes": list(self.possible_causes),
            "recommended_fixes": list(self.recommended_fixes),
            "verification_steps": list(self.verification_steps),
        }


UE_RULES: tuple[UERule, ...] = (
    UERule(
        rule_id="ue_savepackage_linkersave_assertion",
        pattern=r"(Assertion failed:\s*InSaver|LinkerSave\.cpp)",
        category="asset_reference_error",
        severity="critical",
        likely_stage="Cook/Package",
        risk_level="critical",
        possible_causes=(
            "SavePackage received an invalid archive or package writer.",
            "A plugin such as HotPatcher is using UE serialization APIs that changed.",
            "A cooked asset contains stale serialization data or invalid object references.",
            "Saved, Intermediate, or DerivedDataCache contains stale generated state.",
        ),
        recommended_fixes=(
            "Verify the plugin version matches the exact Unreal Engine version.",
            "Clean Saved, Intermediate, and DerivedDataCache before reproducing.",
            "Cook the suspected asset or plugin content in isolation.",
            "Disable the plugin temporarily to confirm whether packaging recovers.",
            "Compare SavePackage or LinkerSave API changes between engine versions.",
        ),
        verification_steps=(
            "Run a clean Cook after cache cleanup.",
            "Package once with the suspected plugin disabled.",
            "Check whether the assertion disappears from the latest log.",
        ),
    ),
    UERule(
        rule_id="ue_assertion_failed",
        pattern=r"Assertion failed:",
        category="runtime_crash",
        severity="critical",
        likely_stage="Runtime",
        risk_level="critical",
        possible_causes=(
            "Engine or project code violated an invariant.",
            "A Blueprint or C++ path passed invalid state into an engine API.",
            "A plugin is incompatible with the current engine version.",
        ),
        recommended_fixes=(
            "Inspect the assertion condition and source file in the same log block.",
            "Review the latest C++ and Blueprint changes touching that code path.",
            "Check plugin compatibility when plugin frames appear near the assertion.",
        ),
        verification_steps=(
            "Reproduce with symbols enabled and capture the full call stack.",
            "Rerun after reverting or isolating the suspected change.",
        ),
    ),
    UERule(
        rule_id="ue_automationtool_error",
        pattern=r"(AutomationTool.*Error|RunUAT.*ERROR|UATHelper:\s*Packaging.*Error)",
        category="packaging_error",
        severity="high",
        likely_stage="Package",
        risk_level="high",
        possible_causes=(
            "AutomationTool failed during BuildCookRun orchestration.",
            "Platform SDK, project settings, or plugin packaging metadata is invalid.",
            "An earlier Cook or Stage error caused UAT to fail later.",
        ),
        recommended_fixes=(
            "Search upward in the log for the first Cook, Stage, or SDK error.",
            "Validate target platform SDK installation and project packaging settings.",
            "Run UAT with verbose logging if the root cause is hidden.",
        ),
        verification_steps=(
            "Rerun packaging after fixing the first upstream error.",
            "Confirm AutomationTool exits with code 0.",
        ),
    ),
    UERule(
        rule_id="ue_packagingresults_error",
        pattern=r"PackagingResults:\s*Error",
        category="packaging_error",
        severity="high",
        likely_stage="Package",
        risk_level="high",
        possible_causes=(
            "Packaging failed after Cook, Stage, or Archive reported an error.",
            "The displayed line may be a summary of an earlier root cause.",
        ),
        recommended_fixes=(
            "Inspect log lines immediately above the PackagingResults error.",
            "Fix the earliest high-severity Cook, asset, plugin, or SDK issue first.",
        ),
        verification_steps=(
            "Package again and verify no PackagingResults errors remain.",
        ),
    ),
    UERule(
        rule_id="ue_unknown_cook_failure",
        pattern=r"Unknown Cook Failure",
        category="packaging_error",
        severity="high",
        likely_stage="Cook",
        risk_level="high",
        possible_causes=(
            "Cook failed before UAT could surface a more specific root cause.",
            "A bad asset, missing reference, plugin error, or Blueprint issue occurred earlier.",
        ),
        recommended_fixes=(
            "Search earlier in the same log for Error, Warning, Ensure, and Blueprint messages.",
            "Cook suspect maps and assets individually.",
            "Clear DerivedDataCache and rerun Cook.",
        ),
        verification_steps=(
            "Run Cook with verbose logging and confirm the failure becomes specific or disappears.",
        ),
    ),
    UERule(
        rule_id="ue_blueprint_compile_error",
        pattern=r"(LogBlueprint.*Error|Blueprint Runtime Error|Compile of .* failed|K2Node)",
        category="blueprint_error",
        severity="medium",
        likely_stage="Build/Cook/Runtime",
        risk_level="medium",
        possible_causes=(
            "A Blueprint node references a missing class, function, pin, or asset.",
            "C++ API changes invalidated generated Blueprint bindings.",
            "A Blueprint compiles in editor but fails during Cook due to load order or references.",
        ),
        recommended_fixes=(
            "Open the named Blueprint and compile it manually.",
            "Refresh nodes and fix broken pins or missing references.",
            "Resave the Blueprint and rerun Cook.",
        ),
        verification_steps=(
            "Confirm the Blueprint compiles with no warnings in editor.",
            "Rerun Cook or packaging and verify the error is gone.",
        ),
    ),
    UERule(
        rule_id="ue_missing_asset",
        pattern=(
            r"(Can't find file|Cannot find file|Failed to load object|"
            r"Failed to load.*'/Game|Missing Asset)"
        ),
        category="asset_reference_error",
        severity="medium",
        likely_stage="Load/Cook",
        risk_level="medium",
        possible_causes=(
            "A hard or soft object reference points to a deleted or moved asset.",
            "Redirectors were not fixed up after moving content.",
            "Cook rules did not include a required asset.",
        ),
        recommended_fixes=(
            "Fix redirectors in the Content Browser.",
            "Search references to the missing asset path.",
            "Add required Cook directories when the asset is intentionally soft-referenced.",
        ),
        verification_steps=(
            "Load the referencing map or Blueprint in editor.",
            "Rerun Cook and confirm the missing asset path is absent from the log.",
        ),
    ),
    UERule(
        rule_id="ue_plugin_module_missing",
        pattern=(
            r"(Plugin .* failed to load|module .* could not be loaded|"
            r"Missing.*\.uplugin|LogPluginManager.*Error)"
        ),
        category="plugin_compatibility",
        severity="medium",
        likely_stage="Build/Startup/Package",
        risk_level="medium",
        possible_causes=(
            "The plugin binary was built for a different engine version or platform.",
            "A module listed in the plugin descriptor is missing or disabled.",
            "The plugin has an unmet dependency.",
        ),
        recommended_fixes=(
            "Rebuild the plugin for the current engine version and target platform.",
            "Check .uplugin module and dependency declarations.",
            "Disable the plugin to confirm whether the project starts or packages.",
        ),
        verification_steps=(
            "Relaunch editor or rerun packaging with the plugin enabled.",
            "Confirm no LogPluginManager error remains.",
        ),
    ),
    UERule(
        rule_id="ue_cpp_compile_error",
        pattern=r"(\berror\s+C\d{4}\b|CompilerResultsLog|\.cpp\(\d+\):\s*error|\.h\(\d+\):\s*error)",
        category="cpp_compile_error",
        severity="high",
        likely_stage="Build",
        risk_level="high",
        possible_causes=(
            "C++ syntax, include, type, or API usage is invalid.",
            "Generated code is stale after a reflected type change.",
            "A module dependency is missing from Build.cs.",
        ),
        recommended_fixes=(
            "Fix the first compiler error before chasing cascaded errors.",
            "Regenerate project files when reflected types or modules changed.",
            "Check Build.cs dependencies for referenced modules.",
        ),
        verification_steps=(
            "Run a clean build for the affected target.",
            "Confirm the compiler error count drops to zero.",
        ),
    ),
    UERule(
        rule_id="ue_shader_ddc_error",
        pattern=r"(ShaderCompileWorker|Failed to compile shader|DerivedDataCache|DDC.*Error)",
        category="build_error",
        severity="medium",
        likely_stage="Cook/Build",
        risk_level="medium",
        possible_causes=(
            "Shader compiler worker failed or crashed.",
            "DerivedDataCache is stale, corrupt, or inaccessible.",
            "A material or shader permutation is invalid for the target platform.",
        ),
        recommended_fixes=(
            "Clear local DerivedDataCache and retry.",
            "Open and re-save suspect materials.",
            "Check platform shader format support.",
        ),
        verification_steps=(
            "Rerun Cook and confirm shader compilation finishes.",
        ),
    ),
    UERule(
        rule_id="ue_platform_sdk_error",
        pattern=r"(Android SDK|NDK|JDK|Windows SDK|Platform SDK.*not found|SDK.*invalid)",
        category="build_error",
        severity="high",
        likely_stage="Build/Package",
        risk_level="high",
        possible_causes=(
            "Required platform SDK is missing or configured incorrectly.",
            "The selected UE version expects a different SDK, NDK, JDK, or Windows SDK version.",
        ),
        recommended_fixes=(
            "Verify SDK paths in Unreal Editor project settings.",
            "Install the SDK version recommended for the UE version.",
            "Restart the shell or editor after changing environment variables.",
        ),
        verification_steps=(
            "Run platform validation from editor settings.",
            "Package again for the same target platform.",
        ),
    ),
    UERule(
        rule_id="ue_pak_iostore_error",
        pattern=(
            r"(UnrealPak.*Error|IoStore.*Error|PakFile.*Error|"
            r"failed to create pak|failed to create container)"
        ),
        category="packaging_error",
        severity="high",
        likely_stage="Stage/Package",
        risk_level="high",
        possible_causes=(
            "Pak or IoStore container generation failed.",
            "A staged file is missing, locked, too long, or has invalid characters.",
            "Packaging settings conflict with the selected target platform.",
        ),
        recommended_fixes=(
            "Check staged file paths near the Pak or IoStore error.",
            "Shorten problematic paths and remove invalid characters.",
            "Retry with Pak or IoStore settings toggled to isolate the issue.",
        ),
        verification_steps=(
            "Rerun packaging and confirm container generation completes.",
        ),
    ),
)


def match_rules(text: str) -> list[UERule]:
    return [rule for rule in UE_RULES if rule.matches(text)]


def rules_to_dict() -> list[dict[str, Any]]:
    return [rule.to_dict() for rule in UE_RULES]
