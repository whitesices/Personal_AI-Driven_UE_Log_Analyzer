# Test Result

The latest full project validation was run after the second-round stabilization work:

```text
python -m pytest
25 passed

ruff check .
All checks passed!

mypy src
Success: no issues found in 13 source files

python -m build
Successfully built source distribution and wheel
```

`python -m build` may require permission outside the local Windows sandbox because isolated build
environments use the system temporary directory.

