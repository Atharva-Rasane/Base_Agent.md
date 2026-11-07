#!/usr/bin/env python3
"""Maintain compact task state without growing the conversation.

Examples:
    python agent_dev_tools/task_checkpoint.py write --goal "Fix retry logic" --done "Reproduced" --next "Add regression test"
    python agent_dev_tools/task_checkpoint.py show
    python agent_dev_tools/task_checkpoint.py clear
"""

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import sys
import tempfile


def render(args: argparse.Namespace) -> str:
    sections = [
        "# Active Task State",
        "",
        f"Updated (UTC): {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Goal",
        args.goal.strip(),
    ]
    for label, entries in (
        ("Completed", args.done),
        ("Decisions", args.decision),
        ("Blockers", args.blocker),
        ("Next", args.next_steps),
    ):
        if entries:
            sections.extend(["", f"## {label}"])
            sections.extend(f"- {entry.strip()}" for entry in entries)
    return "\n".join(sections) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, default=Path("TASK_STATE.md"), help="Local checkpoint path")
    subs = parser.add_subparsers(dest="command", required=True)
    writer = subs.add_parser("write", help="Replace the current task state atomically")
    writer.add_argument("--goal", required=True)
    writer.add_argument("--done", action="append", default=[])
    writer.add_argument("--decision", action="append", default=[])
    writer.add_argument("--blocker", action="append", default=[])
    writer.add_argument("--next", dest="next_steps", action="append", default=[])
    subs.add_parser("show", help="Print the saved task state")
    subs.add_parser("clear", help="Delete the completed task state")
    args = parser.parse_args()
    path = args.file.resolve()
    if args.command == "show":
        if not path.exists():
            print(f"No checkpoint: {path}", file=sys.stderr)
            return 1
        print(path.read_text(encoding="utf-8"), end="")
    elif args.command == "clear":
        path.unlink(missing_ok=True)
        print(f"Cleared: {path}")
    else:
        if not args.goal.strip():
            parser.error("--goal must not be empty")
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as temporary:
                tmp_path = Path(temporary.name)
                temporary.write(render(args))
            os.replace(tmp_path, path)
        finally:
            if tmp_path is not None:
                tmp_path.unlink(missing_ok=True)
        print(f"Saved: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
