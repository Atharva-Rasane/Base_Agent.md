# Token Saving Rules

## Silent desktop notifications
- Use `agent_dev_tools/popup.py` instead of repeatedly asking the user to check whether an operation finished.
- When a task completes, fails, or needs the user's attention, call the popup utility **from the user's graphical desktop environment** with a concise description of what happened:
  - Success: `python agent_dev_tools/popup.py "All tests passed" --title "Codex: Complete" --level success`
  - Failure: `python agent_dev_tools/popup.py "Build failed; see the error summary" --title "Codex: Error" --level error`
  - Attention: `python agent_dev_tools/popup.py "Your approval is required" --title "Codex: Action Needed" --level warning --seconds 15`
- The popup is silent, closes automatically, and returns control immediately. It is a notification only, **not an interactive confirmation dialog**.
- Do not show redundant progress popups or poll continuously. Wait on processes directly or use their completion events where possible.
- If running over SSH, inside a headless container, or without a graphical display, do not assume the popup will be visible on the user's computer. Report status in the normal response instead.
- Do not claim that a popup was displayed unless its display is confirmed; asynchronous launch alone does not establish this.

## Model selection before each task
- Assess task complexity and recommend the least expensive **available** model likely to complete the task reliably.
- Before starting each new task, briefly offer to stop and switch models or override and continue with the current model.
- Never claim the popup tool changes models. Use Codex's normal conversation/approval flow to obtain this decision.
- Do not switch models automatically or invent model names, availability, or costs.

# Debugging diary
- When fixing an error, maintain a concise `Diary.md` entry recording the error, root cause, fix, and verification.
- Consult relevant existing diary entries before investigating a repeated error.
- Do not duplicate existing entries or add entries for routine non-debugging work.
