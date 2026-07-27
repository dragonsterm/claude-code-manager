import json
import os
from pathlib import Path

VALID_TERMINALS = ("powershell", "cmd")


def default_config_path() -> Path:
    """Per-user config location. Frozen exes may live in an unwritable dir."""
    base = os.environ.get("APPDATA")
    root = Path(base) if base else Path.home() / "AppData" / "Roaming"
    current = root / "ClaudeCodeManager" / "config.json"
    # Renamed from "ClaudeManager" in 1.0.1; keep reading the old file until the
    # first save moves it. ponytail: drop this branch once no 1.0.0 users remain.
    legacy = root / "ClaudeManager" / "config.json"
    if not current.exists() and legacy.exists():
        return legacy
    return current


class AppState:
    def __init__(self, config_path=None):
        self.config_path = Path(config_path) if config_path else default_config_path()
        self.current_dir = None
        self.terminal = "powershell"
        self.load()

    def set_directory(self, path: str):
        self.current_dir = str(Path(path).resolve())
        self.save()

    def set_terminal(self, mode: str):
        if mode in VALID_TERMINALS:
            self.terminal = mode
            self.save()

    def is_launch_ready(self) -> bool:
        return self.current_dir is not None and Path(self.current_dir).exists()

    def load(self):
        if not self.config_path.exists():
            return
        try:
            data = json.loads(self.config_path.read_text(encoding="utf-8"))
        except Exception:
            return
        if not isinstance(data, dict):
            return
        # config file is a trust boundary: hand-edited or corrupted values must
        # not reach Path() / the launcher.
        cur = data.get("current_dir")
        self.current_dir = cur if isinstance(cur, str) and cur else None
        term = data.get("terminal")
        self.terminal = term if term in VALID_TERMINALS else "powershell"

    def save(self):
        data = {"current_dir": self.current_dir, "terminal": self.terminal}
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            self.config_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except OSError:
            pass  # a config that cannot persist must never break the launcher
