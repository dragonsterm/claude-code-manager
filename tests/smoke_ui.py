"""Headless-ish smoke check: build the window, verify state wiring, exit."""
import sys
import tkinter as tk
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.ui import ClaudeCodeManagerUI  # noqa: E402

root = tk.Tk()
root.withdraw()
app = ClaudeCodeManagerUI(root)

start_terminal = app.state.terminal
print("switch:", app.btn_switch["text"], "| launch state:", app.btn_launch["state"])
print("launch text:", app.btn_launch["text"])

app.toggle_terminal()
assert app.state.terminal != start_terminal, "toggle did not change terminal"
print("after toggle:", app.btn_switch["text"], "|", app.btn_launch["text"])

app.toggle_terminal()
assert app.state.terminal == start_terminal, "toggle not reversible"

# launch button must be disabled without a directory, enabled with one
app.state.current_dir = None
app.update_ui_state()
assert str(app.btn_launch["state"]) == "disabled"
app.state.current_dir = str(Path(__file__).resolve().parent)
app.update_ui_state()
assert str(app.btn_launch["state"]) == "normal"

# refined-UI structure: divider present, hover bound on every button
assert app.divider.winfo_exists(), "divider missing"
for name in ("btn_new", "btn_change", "btn_launch", "btn_switch"):
    widget = getattr(app, name)
    assert widget.bind("<Enter>"), f"{name} has no hover binding"

# browse dialogs start at the user folder unless a live project dir exists
app.state.current_dir = None
assert app._browse_start_dir() == str(Path.home())
app.state.current_dir = r"C:\does\not\exist"
assert app._browse_start_dir() == str(Path.home()), "stale dir must fall back to home"
here = str(Path(__file__).resolve().parent)
app.state.current_dir = here
assert app._browse_start_dir() == here

# folder-name validation rejects the Windows edge cases
from src.ui import validate_folder_name  # noqa: E402

assert validate_folder_name("MyApp") is None
for bad in ("", "  ", "..", "a/b", "a:b", "CON", "nul.txt", "trail.", " lead"):
    assert validate_folder_name(bad) is not None, f"accepted bad name: {bad!r}"

root.destroy()
print("UI smoke OK")
