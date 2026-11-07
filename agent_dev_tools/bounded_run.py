#!/usr/bin/env python3
"""Run one command, keep its full output on disk, and print a bounded summary.

Examples:
    python agent_dev_tools/bounded_run.py --timeout 120 -- python -m pytest -q
    python agent_dev_tools/bounded_run.py --tail 15 -- git status --short

Pass a command as separate arguments after --; shell expansion is deliberately disabled.
"""

import argparse
from collections import deque
from datetime import datetime, timezone
import os
from pathlib import Path
import signal
import subprocess
import sys


def stop_process(proc: subprocess.Popen) -> None:
    """Terminate the command and its children when possible."""
    if sys.platform == "win32":
        # /T also terminates children; /F is necessary for non-cooperative tools.
        subprocess.run(
            ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            check=False,
        )
    else:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()


def tail_log(log_path: Path, count: int, line_length: int) -> list[str]:
    with log_path.open("r", encoding="utf-8", errors="replace") as stream:
        selected = deque(stream, maxlen=count)
    lines = []
    for raw in selected:
        line = raw.rstrip("\r\n")
        if len(line) > line_length:
            line = line[: line_length - 3] + "..."
        lines.append(line)
    return lines


def run(command: list[str], cwd: Path, log_dir: Path, timeout: float, tail: int, max_line: int) -> int:
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    log_path = log_dir / f"run-{timestamp}-{os.getpid()}.log"

    # Mode 0600 protects logs that accidentally contain credentials or local paths.
    fd = os.open(log_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "wb") as log:
        flags = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if sys.platform == "win32" else {"start_new_session": True}
        try:
            proc = subprocess.Popen(command, cwd=cwd, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, **flags)
        except OSError as exc:
            log.write(f"Could not launch command: {exc}\n".encode("utf-8", errors="replace"))
            status = 127
        else:
            try:
                status = proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                stop_process(proc)
                status = 124
                log.write(f"\nTIMEOUT after {timeout:g} seconds\n".encode())

    print(f"Exit status: {status}")
    print(f"Full log: {log_path.resolve()}")
    print(f"Last {tail} lines (truncated to {max_line} characters each):")
    for line in tail_log(log_path, tail, max_line):
        print(line)
    return status


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cwd", type=Path, default=Path.cwd(), help="Working directory")
    parser.add_argument("--log-dir", type=Path, default=Path(".agent_logs"), help="Directory for complete logs")
    parser.add_argument("--timeout", type=float, default=600, help="Seconds before terminating the process group")
    parser.add_argument("--tail", type=int, default=15, help="Number of final lines to display")
    parser.add_argument("--max-line", type=int, default=240, help="Maximum characters per printed line")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command and arguments following --")
    args = parser.parse_args()
    cmd = args.command[1:] if args.command and args.command[0] == "--" else args.command
    if not cmd:
        parser.error("Specify a command after --")
    if args.timeout <= 0 or not 0 <= args.tail <= 100 or args.max_line < 8:
        parser.error("--timeout must be positive, --tail 0-100, --max-line >= 8")
    cwd = args.cwd.resolve()
    if not cwd.is_dir():
        parser.error("--cwd must be an existing directory")
    log_dir = args.log_dir if args.log_dir.is_absolute() else cwd / args.log_dir
    try:
        return run(cmd, cwd, log_dir, args.timeout, args.tail, args.max_line)
    except (OSError, ValueError) as exc:
        print(f"bounded_run error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
