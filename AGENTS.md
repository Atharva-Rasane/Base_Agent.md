# Agent Operating Rules

## Model selection
- Before each new task, assess complexity and recommend the least expensive available model likely to complete it reliably. Give the user a short **Switch model / Override and continue** choice when a model change is recommended. Do not claim to switch models automatically or invent model availability/pricing.
- Keep the choice brief; do not repeat it for substeps within the same task. Do not begin work until the required decision has been made.

## Commands: preserve them in Makefiles
- **For every project, maintain a `Makefile` for executable development workflows.** Before running a command, inspect existing Make targets and reuse the applicable target.
- Add a descriptively named Make target **before running** any unusual, multi-step, environment-sensitive, or likely-to-recur command. Also record repeated ordinary commands as targets so a later session does not rediscover the syntax.
- Prefer `make <target>` over repeating an inline command. Add a short comment explaining non-obvious flags and prerequisites. Keep targets safe to rerun and fail clearly; avoid hiding errors or using recipes that suppress exit codes.
- Document variables and platform requirements. Never commit credentials, private paths, tokens, or machine-specific secrets. Do not place commands that expose secrets in Make recipes or log them.
- Use the existing project Makefile rather than creating competing build entrypoints. Respect established Make conventions. On Windows, first check whether GNU Make is available; if unavailable, report that limitation instead of repeatedly retrying it.
- Do not force intrinsically interactive, destructive, or one-time secret-bearing commands into a target that can run without confirmation. Document a safe target or explicit manual procedure instead.

## Scope and architecture
- State the expected behavior and verification criteria. Find the authoritative implementation before editing; fix root causes rather than symptoms.
- Make the smallest coherent change. Do not duplicate functionality or introduce unnecessary wrappers, dependencies, global mutable state, or circular imports. Preserve stable interfaces unless the requested task demands a change.
- Stop when all acceptance criteria and relevant verification pass; do not perform unrelated cleanup.

## Context and token efficiency
- Search paths and symbols before opening files. Read only relevant sections; do not dump whole repositories or lengthy logs.
- Prefer existing deterministic tools under `agent_dev_tools/` to implementing new ad hoc utilities. In other projects, use the shared copy in `~/.codex/base-agent/agent_dev_tools/` if project-local tools are absent; do not assume a relative tool path exists. Keep full command logs on disk and provide a bounded excerpt and exit status using the available `bounded_run.py -- <command>` utility. Local runtime logs should not be committed.
- Do not reread unchanged files, repeat searches without new information, or repeatedly check for completion when a blocking wait/event is available.
- Avoid unnecessary subagents. Delegate only independent work with clear deliverables; account for subagent token consumption.

## Quality and verification
- Run focused tests and inspect the diff; expand to full suites only when risk or results justify it.
- On Python repositories use `quality_gate.py` from the installed tools when available (or an equivalent existing quality gate). It checks the changed patch, syntax and Ruff complexity/formatting; a missing Ruff dependency is **incomplete**, not a pass.
- When modifying legacy code, do not claim all pre-existing violations were introduced by the change; use targeted review or a baseline to avoid unrelated rewrites.
- Do not suppress exceptions without explaining why, silently ignore failed commands, or report tests as passing if they were not executed.

## Debugging and continuity
- Reproduce the failure where practical. Run the cheapest experiment that distinguishes plausible causes; do not repeat an unsuccessful attempt without changing the hypothesis.
- Maintain a concise `Diary.md` for recurring or non-obvious errors: symptoms, cause, fix, evidence. Consult it before troubleshooting repeated failures. Do not log routine typos or duplicate existing entries.
- At meaningful milestones on long-running tasks, save `TASK_STATE.md` using the installed `task_checkpoint.py` utility. Include goal, completed work, key decisions, blockers and next actions; do not update it for every tool call. Start a fresh session for unrelated tasks when appropriate.

## Notifications
- Use `popup.py "Message" --title "Codex" --level info` from the installed utilities for task completion, failure, or required attention when running on the user's graphical desktop. It is a silent, auto-closing **notification**, not an approval dialog.
- Do not continuously poll or spam notifications. When headless/remote, report in the normal conversation instead of assuming a popup reaches the user's machine.

## Completion
- Report changed files, tests executed, unresolved problems and follow-up actions in concise form. Do not narrate routine tool calls.
