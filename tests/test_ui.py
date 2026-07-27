from src.ui import format_folder_preview, validate_folder_name


def test_folder_preview_appends_typing_cursor(tmp_path):
    assert format_folder_preview(tmp_path, "MyApp") == str(tmp_path / "MyApp") + "_"


def test_folder_preview_shows_parent_while_empty(tmp_path):
    assert format_folder_preview(tmp_path, "") == str(tmp_path) + "\\_"


def test_folder_preview_strips_invalid_and_trailing_characters(tmp_path):
    assert format_folder_preview(tmp_path, "My/App. ") == str(tmp_path / "MyApp") + "_"


def test_folder_name_validation():
    assert validate_folder_name("MyApp") is None
    assert validate_folder_name("CON")
    assert validate_folder_name("bad/name")
