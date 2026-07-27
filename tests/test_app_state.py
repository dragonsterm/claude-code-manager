import json
import os

from src.app_state import AppState, default_config_path


def test_app_state_defaults(tmp_path):
    state = AppState(config_path=str(tmp_path / "config.json"))
    assert state.terminal == "powershell"
    assert state.current_dir is None
    assert state.is_launch_ready() is False


def test_app_state_set_dir(tmp_path):
    state = AppState(config_path=str(tmp_path / "config.json"))
    state.set_directory(str(tmp_path))
    assert state.current_dir == str(tmp_path.resolve())
    assert state.is_launch_ready() is True


def test_app_state_persists(tmp_path):
    cfg = str(tmp_path / "config.json")
    s1 = AppState(config_path=cfg)
    s1.set_directory(str(tmp_path))
    s1.set_terminal("cmd")

    s2 = AppState(config_path=cfg)
    assert s2.current_dir == str(tmp_path.resolve())
    assert s2.terminal == "cmd"


def test_app_state_rejects_bad_terminal(tmp_path):
    state = AppState(config_path=str(tmp_path / "config.json"))
    state.set_terminal("bash")
    assert state.terminal == "powershell"


def test_default_config_path_is_per_user():
    p = default_config_path()
    assert p.name == "config.json"
    assert p.parent.name in ("ClaudeCodeManager", "ClaudeManager")  # legacy fallback
    appdata = os.environ.get("APPDATA")
    if appdata:
        assert str(p).lower().startswith(appdata.lower())


def test_load_rejects_garbage_values(tmp_path):
    cfg = tmp_path / "config.json"
    cfg.write_text(json.dumps({"current_dir": 123, "terminal": "bash"}), encoding="utf-8")
    state = AppState(config_path=str(cfg))
    assert state.current_dir is None
    assert state.terminal == "powershell"


def test_load_survives_corrupt_file(tmp_path):
    cfg = tmp_path / "config.json"
    cfg.write_text("{not json", encoding="utf-8")
    state = AppState(config_path=str(cfg))
    assert state.current_dir is None
    assert state.terminal == "powershell"


def test_save_creates_missing_parent_dirs(tmp_path):
    cfg = tmp_path / "deep" / "nested" / "config.json"
    state = AppState(config_path=str(cfg))
    state.set_terminal("cmd")
    assert cfg.exists()


def test_save_never_raises_on_unwritable_path(tmp_path):
    # a directory where the config filename already exists as a directory
    blocked = tmp_path / "config.json"
    blocked.mkdir()
    state = AppState(config_path=str(blocked))
    state.set_terminal("cmd")  # must not raise
    assert state.terminal == "cmd"
