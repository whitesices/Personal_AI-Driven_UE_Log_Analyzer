from __future__ import annotations

from pathlib import Path

from ue_log_analyzer.plugin_checker import check_plugin_compatibility


def test_plugin_checker_detects_version_module_and_missing_project_plugin(
    workspace: Path,
) -> None:
    project = workspace / "Project"
    plugin_root = project / "Plugins" / "HotPatcher"
    plugin_root.mkdir(parents=True)
    (project / "Project.uproject").write_text(
        """
{
  "EngineAssociation": "5.3",
  "Plugins": [
    {"Name": "HotPatcher", "Enabled": true},
    {"Name": "MissingProjectPlugin", "Enabled": true}
  ]
}
""".strip(),
        encoding="utf-8",
    )
    (plugin_root / "HotPatcher.uplugin").write_text(
        """
{
  "FriendlyName": "HotPatcher",
  "EngineVersion": "5.1",
  "Modules": [
    {"Name": "HotPatcherRuntime", "Type": "Runtime"}
  ]
}
""".strip(),
        encoding="utf-8",
    )

    report = check_plugin_compatibility(project)

    issue_types = {issue.issue_type for issue in report.issues}
    assert report.plugins_scanned == 1
    assert report.engine_association == "5.3"
    assert "engine_version_mismatch" in issue_types
    assert "module_missing" in issue_types
    assert "enabled_plugin_not_local" in issue_types


def test_plugin_checker_accepts_plugin_module_with_source(workspace: Path) -> None:
    project = workspace / "Project"
    plugin_root = project / "Plugins" / "DemoPlugin"
    module_root = plugin_root / "Source" / "DemoRuntime"
    module_root.mkdir(parents=True)
    (project / "Project.uproject").write_text(
        '{"EngineAssociation":"5.3","Plugins":[{"Name":"DemoPlugin","Enabled":true}]}',
        encoding="utf-8",
    )
    (plugin_root / "DemoPlugin.uplugin").write_text(
        '{"EngineVersion":"5.3","Modules":[{"Name":"DemoRuntime","Type":"Runtime"}]}',
        encoding="utf-8",
    )
    (module_root / "DemoRuntime.Build.cs").write_text(
        "public class DemoRuntime {}",
        encoding="utf-8",
    )

    report = check_plugin_compatibility(project)

    assert report.plugins_scanned == 1
    assert report.issues == []
