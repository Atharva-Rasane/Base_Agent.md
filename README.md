# Base Agent for Codex

A small `AGENTS.md` operating policy and reusable Python utilities for Codex. The utilities use Python 3.10+; only the full code-quality gate optionally requires [Ruff](https://docs.astral.sh/ruff/). GUI notifications also require a local Tkinter desktop environment. Use GNU Make for saved commands.

## Files

- `AGENTS.md` — task/model selection, Makefile discipline, scoped code edits, testing, and notification rules.
- `Makefile` — runnable, named examples (`make help`, `make test`, `make quality-basic`, `make quality`, `make checkpoint-demo`, `make notify-demo`).
- `agent_dev_tools/popup.py` — silent, auto-closing local desktop notification; not an interactive prompt.
- `agent_dev_tools/bounded_run.py` — bounded command output with full local logs and an exit status.
- `agent_dev_tools/quality_gate.py` — check changed Python syntax, Git patch whitespace, Ruff complexity and formatting.
- `agent_dev_tools/task_checkpoint.py` — write, inspect or clear a compact `TASK_STATE.md` checkpoint.

## Setup

1. Clone this repo to a stable location, e.g. `~/.codex/base-agent` (the equivalent is `$HOME\\.codex\\base-agent` on Windows).
2. Copy its `AGENTS.md` to `~/.codex/AGENTS.md` for Codex-wide rules. The standalone repository **does not** apply instructions to unrelated repositories automatically.
3. In other projects, either copy `agent_dev_tools/` and relevant `Makefile` targets into that project or invoke utilities from their absolute path under `~/.codex/base-agent/agent_dev_tools/`. Never assume a relative tool path works in every repo.
4. Add `.agent_logs/`, `TASK_STATE.md`, and Python cache folders to each project's `.gitignore`. Never commit command logs, which can contain sensitive output.
5. To enforce the full Python quality gate, install Ruff with `python -m pip install ruff`. The `--skip-ruff` flag provides explicitly *reduced* verification.

On Windows, GNU Make may need to be installed separately (e.g. with MSYS2 or in WSL). Run desktop `popup.py` from your local Windows Python session, not on a remote SSH host; a remote GUI has no path to your local screen.

## Examples

```bash
make test
make quality-basic
python agent_dev_tools/bounded_run.py --timeout 90 -- python -m unittest discover -s tests -v
python agent_dev_tools/task_checkpoint.py write --goal "Fix network retry" --done "Root cause found" --next "Run focused test"
python agent_dev_tools/popup.py "All tests passed" --title "Codex: Complete" --level success
```

The `Makefile` is the canonical place for commands you run repeatedly or whose flags are unusual. For each target project, preserve relevant commands as named targets **before** repeatedly debugging their syntax. Do not turn secret-bearing or destructive commands into unsafe unattended recipes.

## Limitations

`popup.py` does not change models, and `AGENTS.md` cannot switch models for Codex. The model recommendation is an instruction to ask via the existing chat or approval interface. None of these tools eliminates model context costs; their effectiveness should be measured using comparable tasks, including retries and review time.
