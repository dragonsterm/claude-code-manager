import inspect
import os

from src import launcher
from src.launcher import build_launch_command

TARGET = "C:\\Project\\Demo"


def test_build_launch_command_powershell():
    cmd = build_launch_command("powershell", TARGET)
    assert "powershell.exe" in cmd[0]
    assert TARGET in " ".join(cmd)
    assert "claude" in cmd[-1]


def test_build_launch_command_cmd():
    cmd = build_launch_command("cmd", TARGET)
    assert "cmd.exe" in cmd[0]
    assert TARGET in " ".join(cmd)
    assert "claude" in cmd[-1]


def test_powershell_escapes_apostrophe():
    # C:\Ben's Code is a legal NTFS path; a raw ' would close the quote and the
    # rest of the path would be parsed as PowerShell.
    cmd = build_launch_command("powershell", "C:\\Ben's Code")
    script = cmd[-1]
    assert "Ben''s Code" in script
    # exactly one open + one close quote around the path argument
    assert script.count("'") == 4
    assert script.endswith("; claude")


def test_command_is_argv_list_not_shell_string():
    cmd = build_launch_command("powershell", TARGET)
    assert isinstance(cmd, list)
    assert all(isinstance(part, str) for part in cmd)


def test_powershell_argv0_is_absolute_system32():
    # a bare name lets a dropped powershell.exe beside the exe win the
    # CreateProcess search order
    argv0 = build_launch_command("powershell", TARGET)[0]
    assert os.path.isabs(argv0)
    assert argv0.lower().endswith("\\system32\\windowspowershell\\v1.0\\powershell.exe")


def test_cmd_argv0_is_absolute_system32():
    argv0 = build_launch_command("cmd", TARGET)[0]
    assert os.path.isabs(argv0)
    assert argv0.lower().endswith("\\system32\\cmd.exe")


def test_launch_claude_never_uses_shell():
    src = inspect.getsource(launcher.launch_claude)
    assert "shell=True" not in src
    assert "Popen(cmd" in src
