"""Regression tests for reusable agent tools (stdlib only)."""

import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "agent_dev_tools"


def call(script: str, *args: str, cwd: Path | None = None):
    return subprocess.run(
        [sys.executable, str(TOOLS / script), *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
        timeout=20,
    )


class BoundedRunTests(unittest.TestCase):
    def test_preserves_log_and_exit_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = call(
                "bounded_run.py", "--cwd", tmp, "--tail", "2", "--",
                sys.executable, "-c", "print('OK'); raise SystemExit(3)",
            )
            self.assertEqual(result.returncode, 3, result.stderr)
            self.assertIn("Exit status: 3", result.stdout)
            self.assertIn("OK", result.stdout)
            self.assertEqual(len(list((Path(tmp) / ".agent_logs").glob("*.log"))), 1)

    def test_times_out(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = call(
                "bounded_run.py", "--cwd", tmp, "--timeout", "0.1", "--",
                sys.executable, "-c", "import time; time.sleep(3)",
            )
            self.assertEqual(result.returncode, 124, result.stderr)
            self.assertIn("TIMEOUT", result.stdout)


class CheckpointTests(unittest.TestCase):
    def test_write_show_clear(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = str(Path(tmp) / "TASK_STATE.md")
            self.assertEqual(call("task_checkpoint.py", "--file", state, "write", "--goal", "Fix bug", "--done", "Found cause", "--next", "Test fix").returncode, 0)
            result = call("task_checkpoint.py", "--file", state, "show")
            self.assertEqual(result.returncode, 0)
            self.assertIn("Fix bug", result.stdout)
            self.assertIn("Found cause", result.stdout)
            self.assertIn("Test fix", result.stdout)
            self.assertEqual(call("task_checkpoint.py", "--file", state, "clear").returncode, 0)
            self.assertFalse(Path(state).exists())


class QualityGateTests(unittest.TestCase):
    def test_detects_bad_python_syntax(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            (root / "bad.py").write_text("def broken(:\n", encoding="utf-8")
            result = call("quality_gate.py", "--skip-ruff", cwd=root)
            # A repository without commits does not have HEAD: report the error safely.
            self.assertEqual(result.returncode, 2)

    def test_detects_bad_python_syntax_in_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-q", "--allow-empty", "-m", "initial"], cwd=root, check=True)
            (root / "bad.py").write_text("def broken(:\n", encoding="utf-8")
            result = call("quality_gate.py", "--skip-ruff", cwd=root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("FAIL: Python syntax", result.stderr)


if __name__ == "__main__":
    unittest.main()
