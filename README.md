# Claude Code Manager

A tiny Windows launcher for the [Claude Code](https://claude.com/claude-code) CLI. Pick a
project folder, pick a shell, hit launch — a new console opens in that directory with
`claude` already running.

Python stdlib only (`tkinter`, `subprocess`, `json`, `pathlib`). No dependencies at
runtime, no installer, no background service.

![platform](https://img.shields.io/badge/platform-Windows%2010%2F11-0078D4)
![python](https://img.shields.io/badge/python-3.11%2B-3776AB)
![deps](https://img.shields.io/badge/dependencies-stdlib%20only-brightgreen)
[![license](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

---

## Features

- **Folder switcher** — remembers the last project across restarts.
- **New project** — pick a parent directory, name the folder, it's created and selected.
- **Shell toggle** — PowerShell (default, blue) or CMD (grey), one click.
- **Dark theme** — VS Code `#1E1E1E` surfaces with Claude orange `#D97757` accents.
- **Keyboard driven** — `Enter` launch, `Ctrl+T` toggle shell, `Esc` close.
- **DPI aware** — sharp text on scaled displays.

## Requirements

- Windows 10 or 11
- Python 3.11+ (only to run from source or build; the packaged exe bundles its own)
- `claude` on `PATH` — see the [Claude Code install docs](https://docs.claude.com/en/docs/claude-code/setup)

## Run from source

```powershell
git clone <repo-url> "Claude Manager"
cd "Claude Manager"
python main.py
```

## Build the executable

```powershell
pip install pyinstaller
.\build.ps1
```

`build.ps1` cleans `build/` and `dist/`, runs the unit tests and the UI smoke test,
builds via `ClaudeCodeManager.spec` (onefile, windowed, icon + version resource), and
writes `dist\SHA256SUMS.txt`. Any failing step aborts the build.

Output: `dist\ClaudeCodeManager.exe`

> The build is **unsigned**, so first launch shows the SmartScreen "unknown publisher"
> prompt. Signing is a one-line uncomment in `build.ps1` once a certificate is available.
> See [SECURITY.md](SECURITY.md).

## Usage

1. `+ New Project` or `📁 Change Directory` to select a working directory.
2. Toggle `PS` / `CMD` for the shell you want.
3. `⚡ Launch Claude Code` — the button is disabled until a valid directory is selected.

| Key | Action |
|---|---|
| `Enter` | Launch |
| `Ctrl+T` | Toggle PowerShell / CMD |
| `Esc` | Close |

## Configuration

State lives in `%APPDATA%\ClaudeCodeManager\config.json`:

```json
{
  "current_dir": "C:\\Project\\MyApp",
  "terminal": "powershell"
}
```

Hand-edits are type-checked on load; unknown or malformed values fall back to defaults
rather than reaching the launcher. An unwritable config degrades to non-persistence
instead of erroring.

## Project layout

```
main.py                  entry point (DPI awareness, Tk root)
src/app_state.py         config load/save, launch-readiness
src/launcher.py          shell argv construction + spawn
src/ui.py                Tkinter window, theme, folder-name validation
src/win_theme.py         DPI awareness, dark title bar
tests/                   unit tests, UI smoke test, exe verification
tools/make_icon.py       generates assets/icon.ico
build.ps1                test + build + hash pipeline
ClaudeCodeManager.spec   PyInstaller config
```

## Tests

```powershell
python tests\run_tests.py     # unit tests (stdlib runner, no pytest needed)
python tests\smoke_ui.py      # builds and tears down the window headlessly
.\tests\verify_exe.ps1        # post-build checks on dist\
```

Covers config persistence and corruption handling, PowerShell/CMD command construction,
absolute `System32` interpreter resolution, apostrophe escaping in paths, and folder-name
validation.

## Security

`SECURITY.md` documents the full posture: what the app touches, the unsigned-binary gap,
fixed findings (interpreter hijack via unqualified `argv[0]`, PowerShell quote escape),
and one accepted residual risk (CMD resolves `claude` from the project directory first —
PowerShell mode is unaffected and is the default).

Report issues to the repository owner directly.

## Contributing

Keep it dependency-free and keep the diff small. Before opening a PR:

1. `python tests\run_tests.py` and `python tests\smoke_ui.py` pass.
2. New non-trivial logic ships with a test in `tests/`.
3. Colors come from the `COLOR_*` tokens in `src/ui.py`, not literals.
4. Anything touching path handling or process spawning gets a note in `SECURITY.md`.

By submitting a contribution you agree it is licensed under the MIT License.

## License

[MIT](LICENSE) © 2026 Claude Code Manager contributors.

Bundled third-party components in the packaged executable keep their own licenses:
CPython (PSF), Tcl/Tk (BSD-style), and the PyInstaller bootloader (GPL-2.0 with a
linking exception permitting proprietary and permissively licensed applications).
