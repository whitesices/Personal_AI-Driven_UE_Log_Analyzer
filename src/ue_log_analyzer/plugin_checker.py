from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .reader import LogReaderError, ensure_within_project, resolve_project_root


@dataclass(frozen=True)
class PluginCompatibilityIssue:
    plugin_name: str
    severity: str
    issue_type: str
    message: str
    evidence: str
    recommended_fixes: tuple[str, ...]
    verification_steps: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["recommended_fixes"] = list(self.recommended_fixes)
        data["verification_steps"] = list(self.verification_steps)
        return data


@dataclass(frozen=True)
class PluginCompatibilityReport:
    project_root: Path
    engine_association: str | None
    plugins_scanned: int
    issues: list[PluginCompatibilityIssue] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_root": str(self.project_root),
            "engine_association": self.engine_association,
            "plugins_scanned": self.plugins_scanned,
            "issues": [issue.to_dict() for issue in self.issues],
            "has_blocking_issue": any(
                issue.severity in {"critical", "high"} for issue in self.issues
            ),
        }


def check_plugin_compatibility(project_root: str | Path) -> PluginCompatibilityReport:
    """Inspect UE plugin descriptors inside project_root for compatibility risks."""
    root = resolve_project_root(project_root)
    project_descriptor = _load_project_descriptor(root)
    engine_association = _as_optional_str(project_descriptor.get("EngineAssociation"))
    plugin_files = _find_plugin_descriptors(root)

    issues: list[PluginCompatibilityIssue] = []
    for descriptor_path in plugin_files:
        descriptor = _read_json_descriptor(descriptor_path, root)
        plugin_name = _plugin_name(descriptor_path, descriptor)
        issues.extend(
            _check_plugin_descriptor(
                root=root,
                descriptor_path=descriptor_path,
                descriptor=descriptor,
                plugin_name=plugin_name,
                engine_association=engine_association,
            )
        )

    issues.extend(_check_project_enabled_plugins(root, project_descriptor, plugin_files))

    return PluginCompatibilityReport(
        project_root=root,
        engine_association=engine_association,
        plugins_scanned=len(plugin_files),
        issues=issues,
    )


def _load_project_descriptor(root: Path) -> dict[str, Any]:
    uproject_files = sorted(root.glob("*.uproject"))
    if not uproject_files:
        return {}
    return _read_json_descriptor(uproject_files[0], root)


def _find_plugin_descriptors(root: Path) -> list[Path]:
    plugins_dir = root / "Plugins"
    if not plugins_dir.exists() or not plugins_dir.is_dir():
        return []
    return [
        ensure_within_project(path, root)
        for path in sorted(plugins_dir.rglob("*.uplugin"))
        if path.is_file()
    ]


def _read_json_descriptor(path: Path, root: Path) -> dict[str, Any]:
    safe_path = ensure_within_project(path, root)
    try:
        raw_text = safe_path.read_text(encoding="utf-8-sig", errors="replace")
        value = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise LogReaderError(f"Invalid JSON descriptor: {safe_path}: {exc}") from exc
    if not isinstance(value, dict):
        raise LogReaderError(f"Descriptor must be a JSON object: {safe_path}")
    return value


def _plugin_name(path: Path, descriptor: dict[str, Any]) -> str:
    friendly_name = _as_optional_str(descriptor.get("FriendlyName"))
    return friendly_name or path.stem


def _check_plugin_descriptor(
    root: Path,
    descriptor_path: Path,
    descriptor: dict[str, Any],
    plugin_name: str,
    engine_association: str | None,
) -> list[PluginCompatibilityIssue]:
    issues: list[PluginCompatibilityIssue] = []
    engine_version = _as_optional_str(descriptor.get("EngineVersion"))
    if engine_association and engine_version and not _engine_versions_compatible(
        engine_association,
        engine_version,
    ):
        issues.append(
            PluginCompatibilityIssue(
                plugin_name=plugin_name,
                severity="high",
                issue_type="engine_version_mismatch",
                message="Plugin EngineVersion does not match project EngineAssociation.",
                evidence=f"project={engine_association}, plugin={engine_version}",
                recommended_fixes=(
                    "Install a plugin build that targets the same Unreal Engine version.",
                    "Rebuild the plugin from source for this engine version.",
                    "Check the plugin vendor release notes for version-specific changes.",
                ),
                verification_steps=(
                    "Restart the editor and confirm there are no LogPluginManager errors.",
                    "Run packaging again and confirm no module compatibility errors remain.",
                ),
            )
        )

    modules = descriptor.get("Modules", [])
    if modules is not None and not isinstance(modules, list):
        issues.append(
            PluginCompatibilityIssue(
                plugin_name=plugin_name,
                severity="medium",
                issue_type="invalid_modules_schema",
                message="Plugin descriptor has a non-list Modules field.",
                evidence=str(descriptor_path.relative_to(root).as_posix()),
                recommended_fixes=(
                    "Fix the .uplugin Modules field so it is an array of module objects.",
                ),
                verification_steps=("Reload the plugin descriptor in Unreal Editor.",),
            )
        )
        modules = []

    for module in modules:
        if not isinstance(module, dict):
            continue
        module_name = _as_optional_str(module.get("Name"))
        if not module_name:
            continue
        if not _module_has_source_or_binary(root, descriptor_path, module_name):
            issues.append(
                PluginCompatibilityIssue(
                    plugin_name=plugin_name,
                    severity="high",
                    issue_type="module_missing",
                    message=f"Plugin module `{module_name}` has no Source or Binaries artifact.",
                    evidence=str(descriptor_path.relative_to(root).as_posix()),
                    recommended_fixes=(
                        "Restore the missing plugin module source or prebuilt binary.",
                        "Regenerate project files and rebuild the plugin.",
                        "Remove or disable the module from the .uplugin descriptor if obsolete.",
                    ),
                    verification_steps=(
                        "Build the project target that loads the plugin.",
                        "Confirm the latest log has no module load failure for this plugin.",
                    ),
                )
            )

    return issues


def _check_project_enabled_plugins(
    root: Path,
    project_descriptor: dict[str, Any],
    plugin_files: list[Path],
) -> list[PluginCompatibilityIssue]:
    local_plugin_names = {path.stem for path in plugin_files}
    issues: list[PluginCompatibilityIssue] = []
    plugins = project_descriptor.get("Plugins", [])
    if not isinstance(plugins, list):
        return issues

    for plugin in plugins:
        if not isinstance(plugin, dict):
            continue
        name = _as_optional_str(plugin.get("Name"))
        enabled = bool(plugin.get("Enabled", False))
        if not name or not enabled:
            continue
        if name not in local_plugin_names:
            issues.append(
                PluginCompatibilityIssue(
                    plugin_name=name,
                    severity="medium",
                    issue_type="enabled_plugin_not_local",
                    message=(
                        "Project enables a plugin that is not present under "
                        "the local Plugins folder."
                    ),
                    evidence=f"{name} enabled in .uproject",
                    recommended_fixes=(
                        "Confirm whether this is an engine plugin or a missing project plugin.",
                        "Install the plugin under Plugins if it is project-local.",
                        "Disable the plugin in the .uproject if it is no longer needed.",
                    ),
                    verification_steps=(
                        "Launch the editor and confirm no missing plugin dialog appears.",
                        "Run packaging and confirm no LogPluginManager error remains.",
                    ),
                )
            )
    return issues


def _module_has_source_or_binary(root: Path, descriptor_path: Path, module_name: str) -> bool:
    plugin_root = descriptor_path.parent
    source_build_cs = plugin_root / "Source" / module_name / f"{module_name}.Build.cs"
    binaries_dir = plugin_root / "Binaries"
    if source_build_cs.exists() and ensure_within_project(source_build_cs, root).is_file():
        return True
    if binaries_dir.exists() and ensure_within_project(binaries_dir, root).is_dir():
        module_prefix = module_name.lower()
        for path in binaries_dir.rglob("*"):
            safe_path = ensure_within_project(path, root)
            if safe_path.is_file() and safe_path.name.lower().startswith(module_prefix):
                return True
    return False


def _engine_versions_compatible(project_version: str, plugin_version: str) -> bool:
    return _major_minor(project_version) == _major_minor(plugin_version)


def _major_minor(version: str) -> tuple[str, str]:
    parts = version.strip().split(".")
    major = parts[0] if parts else ""
    minor = parts[1] if len(parts) > 1 else ""
    return major, minor


def _as_optional_str(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None
