import os
import subprocess
from pathlib import Path


def _ps_quote(value: str) -> str:
    """Escape for a PowerShell single-quoted string. Apostrophes are legal in
    NTFS paths (C:\\Ben's Code) and would otherwise close the quote early."""
    return value.replace("'", "''")


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
    target_path = str(Path(target_dir).resolve())
    if terminal_type == "powershell":
        return [
            powershell_path(),
            "-NoExit",
            "-Command",
            f"Set-Location -LiteralPath '{_ps_quote(target_path)}'; claude",
        ]
    return [
        cmd_path(),
        "/k",
        f'cd /d "{target_path}" && claude',
    ]


def launch_claude(terminal_type: str, target_dir: str):
    cmd = build_launch_command(terminal_type, target_dir)
    # argv list, no shell interpolation
    return subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
