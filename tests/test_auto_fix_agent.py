from __future__ import annotations

from pathlib import Path

from ue_log_analyzer.auto_fix_agent import generate_auto_fix_plan


def test_auto_fix_agent_combines_log_plugin_and_blueprint_diagnostics(
    workspace: Path,
) -> None:
    project = workspace / "Project"
    logs = project / "Saved" / "Logs"
    plugin_root = project / "Plugins" / "DemoPlugin"
    logs.mkdir(parents=True)
    plugin_root.mkdir(parents=True)
    (project / "Project.uproject").write_text(
        '{"EngineAssociation":"5.3","Plugins":[{"Name":"DemoPlugin","Enabled":true}]}',
        encoding="utf-8",
    )
    (plugin_root / "DemoPlugin.uplugin").write_text(
        '{"EngineVersion":"5.1","Modules":[{"Name":"DemoRuntime","Type":"Runtime"}]}',
        encoding="utf-8",
    )
    (logs / "Project.log").write_text(
        "\n".join(
            [
                "PackagingResults: Error: Unknown Cook Failure",
                "LogBlueprint: Error: Compile of BP_Player failed. "
                "Could not find function GiveDamage.",
            ]
        ),
        encoding="utf-8",
    )

    plan = generate_auto_fix_plan(project)

    categories = {suggestion.category for suggestion in plan.suggestions}
    assert "packaging_error" in categories
    assert "plugin_compatibility" in categories
    assert "blueprint_error" in categories
    assert any("does not modify" in note for note in plan.suggestions[0].safety_notes)
