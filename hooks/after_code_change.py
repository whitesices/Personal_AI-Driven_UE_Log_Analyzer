from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def build_pytest_command(extra_args: list[str] | None = None) -> list[str]:
    return [sys.executable, "-m", "pytest", *(extra_args or [])]


def run_pytest(extra_args: list[str] | None = None) -> int:
    command = build_pytest_command(extra_args)
    completed = subprocess.run(command, cwd=repo_root(), check=False)
    return int(completed.returncode)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run project tests after AI code changes.")
    parser.add_argument("pytest_args", nargs="*", help="Extra arguments passed to pytest.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run_pytest(args.pytest_args)


if __name__ == "__main__":
    raise SystemExit(main())

