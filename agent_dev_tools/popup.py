#!/usr/bin/env python3
"""Show a silent, self-closing desktop notification without third-party packages.

Examples:
    python agent_dev_tools/popup.py "All 12 tests passed" --title "Codex: Complete" --level success
    python agent_dev_tools/popup.py "The build failed" --level error --seconds 15

The normal command launches the popup in a separate process and returns immediately.
Run with --foreground to debug GUI errors.
"""

import argparse
import os
from pathlib import Path
import subprocess
import sys


COLORS = {
    "info": "#60a5fa",
    "success": "#34d399",
    "warning": "#fbbf24",
    "error": "#fb7185",
}


def show_popup(title: str, message: str, level: str, seconds: float) -> int:
    try:
        import tkinter as tk

        window = tk.Tk()
    except Exception as exc:
        print(f"Cannot show desktop popup: {exc}", file=sys.stderr)
        return 2

    window.withdraw()
    window.overrideredirect(True)
    window.attributes("-topmost", True)
    window.configure(bg=COLORS[level])

    background = "#172033"
    panel = tk.Frame(window, bg=background, padx=16, pady=12)
    panel.pack(fill="both", expand=True, padx=(5, 1), pady=1)

    top = tk.Frame(panel, bg=background)
    top.pack(fill="x")
    tk.Label(
        top, text=title[:72], bg=background, fg="#f8fafc",
        font=("Segoe UI", 11, "bold"), anchor="w",
    ).pack(side="left", fill="x", expand=True)
    tk.Button(
        top, text="×", command=window.destroy, bg=background, fg="#cbd5e1",
        bd=0, font=("Segoe UI", 12), activebackground=background,
        activeforeground="#ffffff", cursor="hand2",
    ).pack(side="right")
    tk.Label(
        panel, text=message[:600], bg=background, fg="#e2e8f0",
        font=("Segoe UI", 10), justify="left", anchor="w",
        wraplength=360,
    ).pack(fill="x", pady=(7, 2))

    window.update_idletasks()
    width = 430
    height = window.winfo_reqheight()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window.geometry(f"{width}x{height}+{max(0, screen_width-width-24)}+{max(0, screen_height-height-65)}")
    window.after(int(seconds * 1000), window.destroy)
    window.deiconify()
    window.mainloop()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("message", help="Short description of what happened")
    parser.add_argument("--title", default="Codex", help="Notification title")
    parser.add_argument("--level", choices=COLORS, default="info")
    parser.add_argument("--seconds", type=float, default=8, help="Seconds before closing (1-120)")
    parser.add_argument("--foreground", action="store_true", help="Show in this process for debugging")
    parser.add_argument("--_child", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    if not 1 <= args.seconds <= 120:
        parser.error("--seconds must be between 1 and 120")
    if sys.platform != "win32" and not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        print("No local graphical desktop is available; popup not shown.", file=sys.stderr)
        return 2
    if args._child or args.foreground:
        return show_popup(args.title, args.message, args.level, args.seconds)

    interpreter = sys.executable
    if sys.platform == "win32":
        pythonw = Path(interpreter).with_name("pythonw.exe")
        if pythonw.exists():
            interpreter = str(pythonw)

    command = [
        interpreter, str(Path(__file__).resolve()), args.message,
        "--title", args.title, "--level", args.level,
        "--seconds", str(args.seconds), "--_child",
    ]
    options = {
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "close_fds": True,
    }
    if sys.platform == "win32":
        options["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
    else:
        options["start_new_session"] = True
    try:
        subprocess.Popen(command, **options)
    except OSError as exc:
        print(f"Could not launch desktop popup: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
