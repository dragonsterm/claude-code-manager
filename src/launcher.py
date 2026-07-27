import os
import subprocess
from pathlib import Path


def _system32(*parts) -> str:
    """Absolute path under %SystemRoot%\\System32.

    CreateProcess with a bare name searches the calling process directory and
    the CWD before System32, so a dropped powershell.exe next to the exe would
    win. Always pass argv[0] fully qualified.
    """
    root = os.environ.get("SystemRoot") or "C:\\Windows"
    return str(Path(root, "System32", *parts))


def powershell_path() -> str:
    exe = _system32("WindowsPowerShell", "v1.0", "powershell.exe")
    return exe if Path(exe).exists() else "powershell.exe"


def cmd_path() -> str:
    exe = _system32("cmd.exe")
    return exe if Path(exe).exists() else "cmd.exe"


def build_launch_command(terminal_type: str, target_dir: str) -> list:
    if terminal_type == "powershell":
        return [
            powershell_path(),
            "-NoExit",
            "-Command",
            "claude",
        ]
    return [
        cmd_path(),
        "/k",
        "claude",
    ]


def launch_claude(terminal_type: str, target_dir: str):
    cmd = build_launch_command(terminal_type, target_dir)
    # `cwd` sets the child process directory without CMD/PowerShell parsing.
    return subprocess.Popen(
        cmd,
        cwd=str(Path(target_dir).resolve()),
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )
