from pathlib import Path

from anytask_scraper.client import AnytaskClient


def test_save_and_load_session(tmp_path: Path) -> None:
    session_file = tmp_path / "session.json"

    with AnytaskClient("user", "pass") as client:
        client._client.cookies.set("sessionid", "abc123", domain="anytask.org", path="/")
        client._client.cookies.set("csrftoken", "token456", domain="anytask.org", path="/")
        client.save_session(session_file)

    with AnytaskClient() as loaded:
        ok = loaded.load_session(session_file)
        assert ok

        cookies = {c.name: c.value for c in loaded._client.cookies.jar}
        assert cookies["sessionid"] == "abc123"
        assert cookies["csrftoken"] == "token456"


def test_load_session_returns_false_for_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing_session.json"
    with AnytaskClient() as client:
        assert client.load_session(missing) is False
