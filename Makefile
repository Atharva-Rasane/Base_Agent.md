# Reusable commands for the Base_Agent.md template.
# Python 3.10+ and GNU Make. On Windows use an installed GNU Make (e.g. Git Bash/WSL).
PYTHON ?= python

.PHONY: help test quality quality-basic notify-demo checkpoint-demo

help:
	@echo "make test             - Run utility regression tests with bounded output"
	@echo "make quality          - Check changed Python files (Ruff required when changed)"
	@echo "make quality-basic    - Check diff whitespace and Python syntax without Ruff"
	@echo "make notify-demo      - Show a silent desktop notification (GUI required)"
	@echo "make checkpoint-demo  - Write, display, and clear a sample task checkpoint"

# Run tests through bounded_run: full output stays under .agent_logs/.
test:
	$(PYTHON) agent_dev_tools/bounded_run.py --timeout 120 --tail 30 -- $(PYTHON) -m unittest discover -s tests -v

quality:
	$(PYTHON) agent_dev_tools/quality_gate.py

quality-basic:
	$(PYTHON) agent_dev_tools/quality_gate.py --skip-ruff

notify-demo:
	$(PYTHON) agent_dev_tools/popup.py "The agent notification tool is available" --title "Codex: Demo" --level success

checkpoint-demo:
	$(PYTHON) agent_dev_tools/task_checkpoint.py write --goal "Demonstrate checkpointing" --done "Utility invoked" --next "Continue the task"
	$(PYTHON) agent_dev_tools/task_checkpoint.py show
	$(PYTHON) agent_dev_tools/task_checkpoint.py clear
