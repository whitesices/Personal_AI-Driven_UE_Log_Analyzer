# Test Report

## 1. Test Commands

```bash
python -m pytest
ruff check .
mypy src
```

## 2. Pytest Coverage

Current pytest coverage includes:

- Latest UE log discovery.
- Tail read limit.
- Path traversal rejection for input logs.
- Project-relative log paths.
- Clean log handling.
- UE professional rule matching.
- HotPatcher / LinkerSave / InSaver assertion scenario.
- PackagingResults and Unknown Cook Failure scenario.
- Blueprint compile error scenario.
- Missing Asset scenario.
- Markdown report required sections.
- MCP-style tools and dispatcher.
- MCP stdio adapter registered tool names.
- MCP stdio server creation when MCP SDK is installed.
- `scan_ue_project_structure`.
- CLI output path boundary checks.
- Hook command construction and pre-commit scan behavior.

## 3. Latest Result

```text
python -m pytest
25 passed in 0.87s

ruff check .
All checks passed!

mypy src
Success: no issues found in 13 source files

python -m build
Successfully built source distribution and wheel
```

## 4. Environment Notes

The local Windows sandbox previously blocked pytest default temporary/cache directories.

Mitigation:

- Tests use a local `test_workspace` fixture.
- The fixture cleans each case with `shutil.rmtree(..., ignore_errors=True)`.
- `.gitignore` excludes generated test workspace and pytest cache artifacts.
- `pyproject.toml` disables pytest cache provider.

## 5. Quality Gates

Second-round engineering gates:

- `python -m pytest`
- `ruff check .`
- `mypy src`
- `python -m build`
- GitHub Actions CI running pytest, ruff, and mypy.

`python -m build` required escalated execution in the local Windows sandbox because isolated
build environments were blocked in the default temp directory. This is an environment constraint,
not a package configuration issue.
