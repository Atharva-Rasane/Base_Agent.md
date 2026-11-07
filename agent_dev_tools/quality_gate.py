#!/usr/bin/env python3
"""Check changed Python files, patch integrity, and optional Ruff quality rules.

Run in the target repository from its root. A passing result applies to changed
files only, not to all pre-existing code. Install Ruff for the complete gate:
    python -m pip install ruff

Examples:
    python agent_dev_tools/quality_gate.py
    python agent_dev_tools/quality_gate.py --base HEAD~1
    python agent_dev_tools/quality_gate.py --skip-ruff  # explicit, reduced verification
"""

import argparse
import importlib.util
from pathlib import Path
import subprocess
import sys


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def get_changed(base: str) -> list[Path]:
    changed = set()
    commands = [
        ("diff", "--name-only", "-z", "--diff-filter=ACMRT", base, "--"),
        ("ls-files", "--others", "--exclude-standard", "-z"),
    ]
    for command in commands:
        result = git(*command)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.decode(errors="replace").strip())
        for raw in result.stdout.split(b"\x00"):
            if raw:
                changed.add(Path(raw.decode("utf-8", errors="surrogateescape")))
    return sorted(p for p in changed if p.suffix == ".py" and p.exists() and p.is_file())


def check_git_diff() -> bool:
    good = True
    for command in (("diff", "--check"), ("diff", "--cached", "--check")):
        result = git(*command)
        if result.returncode:
            print(f"FAIL: git {' '.join(command)}", file=sys.stderr)
            print(result.stdout.decode(errors="replace"), end="", file=sys.stderr)
            print(result.stderr.decode(errors="replace"), end="", file=sys.stderr)
            good = False
    return good


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="HEAD", help="Git revision to compare to, default HEAD")
    parser.add_argument("--skip-ruff", action="store_true", help="Explicitly bypass Ruff; syntax/whitespace only")
    args = parser.parse_args()
    repo = git("rev-parse", "--is-inside-work-tree")
    if repo.returncode or repo.stdout.strip() != b"true":
        parser.error("run inside a Git working tree")
    try:
        changed = get_changed(args.base)
    except RuntimeError as exc:
        print(f"Cannot inspect changed files: {exc}", file=sys.stderr)
        return 2
    print(f"Changed Python files: {len(changed)}")
    passed = check_git_diff()
    for path in changed:
        try:
            source = path.read_bytes()
            compile(source, str(path), "exec")
        except (SyntaxError, UnicodeError, OSError, ValueError) as exc:
            print(f"FAIL: Python syntax {path}: {exc}", file=sys.stderr)
            passed = False
    if passed:
        print("PASS: Git patch whitespace and Python syntax")
    if not changed:
        print("No changed Python files require Ruff checks")
        return 0 if passed else 1
    if args.skip_ruff:
        print("INCOMPLETE: Ruff checks intentionally skipped")
        return 0 if passed else 1
    if importlib.util.find_spec("ruff") is None:
        print("INCOMPLETE: Ruff is missing. Install with 'python -m pip install ruff' or explicitly use --skip-ruff.", file=sys.stderr)
        return 2
    paths = [str(p) for p in changed]
    for tool_args in (
        ("check", "--select", "C901,PLR0912,PLR0913,PLR0915"),
        ("format", "--check"),
    ):
        check = subprocess.run([sys.executable, "-m", "ruff", *tool_args, *paths], check=False)
        if check.returncode:
            passed = False
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
