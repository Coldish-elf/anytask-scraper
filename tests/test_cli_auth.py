from pathlib import Path

from anytask_scraper.cli import _load_credentials_file


def test_load_credentials_from_json(tmp_path: Path) -> None:
    creds = tmp_path / "creds.json"
    creds.write_text('{"username": "alice", "password": "secret"}', encoding="utf-8")

    username, password = _load_credentials_file(str(creds))

    assert username == "alice"
    assert password == "secret"


def test_load_credentials_from_key_value(tmp_path: Path) -> None:
    creds = tmp_path / "creds.env"
    creds.write_text("username=bob\npassword=pass123\n", encoding="utf-8")

    username, password = _load_credentials_file(str(creds))

    assert username == "bob"
    assert password == "pass123"


def test_load_credentials_from_two_lines_fallback(tmp_path: Path) -> None:
    creds = tmp_path / "creds.txt"
    creds.write_text("charlie\nqwerty\n", encoding="utf-8")

    username, password = _load_credentials_file(str(creds))

    assert username == "charlie"
    assert password == "qwerty"
