from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from anytask_scraper.api import create_app
from anytask_scraper.client import WriteError
from anytask_scraper.models import WriteResult


@pytest.fixture()
def _setup():
    """Create a test app with mocked client, entered via TestClient context."""
    application = create_app()
    mock_client = MagicMock()
    mock_client._authenticated = True

    with TestClient(application) as tc:
        state = application.state.anytask
        state._client = mock_client
        yield tc, mock_client


@pytest.fixture()
def client(_setup):
    return _setup[0]


@pytest.fixture()
def mock_anytask_client(_setup):
    return _setup[1]


class TestSetGradeEndpoint:
    def test_successful_grade(self, client, mock_anytask_client) -> None:
        mock_anytask_client.set_grade.return_value = WriteResult(
            success=True,
            action="grade",
            issue_id=500003,
            value="10.0",
            message="Grade set to 10.0",
        )

        resp = client.post("/submissions/500003/grade", json={"grade": 10.0})

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["action"] == "grade"
        assert data["issue_id"] == 500003
        assert data["value"] == "10.0"
        mock_anytask_client.set_grade.assert_called_once_with(500003, 10.0, comment="")

    def test_grade_with_comment(self, client, mock_anytask_client) -> None:
        mock_anytask_client.set_grade.return_value = WriteResult(
            success=True,
            action="grade",
            issue_id=500003,
            value="10.0",
        )

        resp = client.post(
            "/submissions/500003/grade",
            json={"grade": 10.0, "comment": "Well done"},
        )

        assert resp.status_code == 200
        mock_anytask_client.set_grade.assert_called_once_with(500003, 10.0, comment="Well done")

    def test_grade_write_error(self, client, mock_anytask_client) -> None:
        mock_anytask_client.set_grade.side_effect = WriteError("Missing CSRF token")

        resp = client.post("/submissions/500003/grade", json={"grade": 10.0})

        assert resp.status_code == 500
        assert "Missing CSRF token" in resp.json()["detail"]

    def test_grade_missing_body(self, client) -> None:
        resp = client.post("/submissions/500003/grade", json={})

        assert resp.status_code == 422


class TestSetStatusEndpoint:
    def test_successful_status_by_name(self, client, mock_anytask_client) -> None:
        mock_anytask_client.set_status.return_value = WriteResult(
            success=True,
            action="status",
            issue_id=500003,
            value="5",
        )

        resp = client.post(
            "/submissions/500003/status",
            json={"status": "accepted"},
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["action"] == "status"
        mock_anytask_client.set_status.assert_called_once_with(500003, 5, comment="")

    def test_status_by_number(self, client, mock_anytask_client) -> None:
        mock_anytask_client.set_status.return_value = WriteResult(
            success=True,
            action="status",
            issue_id=500003,
            value="3",
        )

        resp = client.post(
            "/submissions/500003/status",
            json={"status": "3"},
        )

        assert resp.status_code == 200
        mock_anytask_client.set_status.assert_called_once_with(500003, 3, comment="")

    def test_status_review(self, client, mock_anytask_client) -> None:
        mock_anytask_client.set_status.return_value = WriteResult(
            success=True,
            action="status",
            issue_id=500003,
            value="3",
        )

        resp = client.post(
            "/submissions/500003/status",
            json={"status": "review"},
        )

        assert resp.status_code == 200
        mock_anytask_client.set_status.assert_called_once_with(500003, 3, comment="")

    def test_status_rework(self, client, mock_anytask_client) -> None:
        mock_anytask_client.set_status.return_value = WriteResult(
            success=True,
            action="status",
            issue_id=500003,
            value="4",
        )

        resp = client.post(
            "/submissions/500003/status",
            json={"status": "rework"},
        )

        assert resp.status_code == 200
        mock_anytask_client.set_status.assert_called_once_with(500003, 4, comment="")

    def test_invalid_status_name(self, client) -> None:
        resp = client.post(
            "/submissions/500003/status",
            json={"status": "invalid"},
        )

        assert resp.status_code == 422
        assert "Invalid status" in resp.json()["detail"]

    def test_status_with_comment(self, client, mock_anytask_client) -> None:
        mock_anytask_client.set_status.return_value = WriteResult(
            success=True,
            action="status",
            issue_id=500003,
            value="4",
        )

        resp = client.post(
            "/submissions/500003/status",
            json={"status": "rework", "comment": "Please fix section 2"},
        )

        assert resp.status_code == 200
        mock_anytask_client.set_status.assert_called_once_with(
            500003, 4, comment="Please fix section 2"
        )

    def test_status_write_error(self, client, mock_anytask_client) -> None:
        mock_anytask_client.set_status.side_effect = WriteError("CSRF expired")

        resp = client.post(
            "/submissions/500003/status",
            json={"status": "accepted"},
        )

        assert resp.status_code == 500


class TestAddCommentEndpoint:
    def test_successful_comment(self, client, mock_anytask_client) -> None:
        mock_anytask_client.add_comment.return_value = WriteResult(
            success=True,
            action="comment",
            issue_id=500003,
            value="Looks good!",
            message="Comment added",
        )

        resp = client.post(
            "/submissions/500003/comment",
            json={"comment": "Looks good!"},
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["action"] == "comment"
        mock_anytask_client.add_comment.assert_called_once_with(500003, "Looks good!")

    def test_comment_write_error(self, client, mock_anytask_client) -> None:
        mock_anytask_client.add_comment.side_effect = WriteError("No form")

        resp = client.post(
            "/submissions/500003/comment",
            json={"comment": "Hello"},
        )

        assert resp.status_code == 500
        assert "No form" in resp.json()["detail"]

    def test_comment_missing_body(self, client) -> None:
        resp = client.post("/submissions/500003/comment", json={})

        assert resp.status_code == 422
