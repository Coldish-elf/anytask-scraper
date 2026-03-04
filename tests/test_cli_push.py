from __future__ import annotations

import argparse
from unittest.mock import MagicMock, patch

import pytest

from anytask_scraper.cli import _build_parser, _resolve_status, _run_push
from anytask_scraper.models import WriteResult


class TestPushParser:
    def setup_method(self) -> None:
        self.parser = _build_parser()

    def test_push_grade_args(self) -> None:
        args = self.parser.parse_args(
            ["push", "grade", "--issue-id", "500003", "--grade", "10.5", "--comment", "Nice"]
        )
        assert args.command == "push"
        assert args.push_action == "grade"
        assert args.issue_id == 500003
        assert args.grade == 10.5
        assert args.comment == "Nice"
        assert args.dry_run is False

    def test_push_grade_dry_run(self) -> None:
        args = self.parser.parse_args(
            ["push", "grade", "--issue-id", "500003", "--grade", "8", "--dry-run"]
        )
        assert args.dry_run is True

    def test_push_status_args(self) -> None:
        args = self.parser.parse_args(
            ["push", "status", "--issue-id", "500003", "--status", "accepted"]
        )
        assert args.push_action == "status"
        assert args.status == "accepted"
        assert args.comment == ""

    def test_push_status_with_comment(self) -> None:
        args = self.parser.parse_args(
            [
                "push",
                "status",
                "--issue-id",
                "500003",
                "--status",
                "rework",
                "--comment",
                "Please revise section 2",
            ]
        )
        assert args.status == "rework"
        assert args.comment == "Please revise section 2"

    def test_push_comment_args(self) -> None:
        args = self.parser.parse_args(
            ["push", "comment", "--issue-id", "500003", "--comment", "Looks good!"]
        )
        assert args.push_action == "comment"
        assert args.comment == "Looks good!"

    def test_push_grade_requires_issue_id(self) -> None:
        with pytest.raises(SystemExit):
            self.parser.parse_args(["push", "grade", "--grade", "10"])

    def test_push_grade_requires_grade(self) -> None:
        with pytest.raises(SystemExit):
            self.parser.parse_args(["push", "grade", "--issue-id", "500003"])

    def test_push_status_requires_status(self) -> None:
        with pytest.raises(SystemExit):
            self.parser.parse_args(["push", "status", "--issue-id", "500003"])

    def test_push_comment_requires_comment(self) -> None:
        with pytest.raises(SystemExit):
            self.parser.parse_args(["push", "comment", "--issue-id", "500003"])


class TestResolveStatus:
    def test_review(self) -> None:
        assert _resolve_status("review") == 3

    def test_rework(self) -> None:
        assert _resolve_status("rework") == 4

    def test_accepted(self) -> None:
        assert _resolve_status("accepted") == 5

    def test_numeric_string(self) -> None:
        assert _resolve_status("3") == 3

    def test_invalid_raises(self) -> None:
        with pytest.raises((argparse.ArgumentTypeError, ValueError)):
            _resolve_status("invalid")


class TestRunPush:
    def _make_args(self, **overrides: object) -> MagicMock:
        defaults = {
            "push_action": "grade",
            "issue_id": 500003,
            "grade": 10.0,
            "comment": "",
            "dry_run": False,
        }
        defaults.update(overrides)
        args = MagicMock()
        for k, v in defaults.items():
            setattr(args, k, v)
        return args

    def test_grade_calls_set_grade(self) -> None:
        client = MagicMock()
        client.set_grade.return_value = WriteResult(
            success=True,
            action="grade",
            issue_id=500003,
            value="10.0",
            message="Grade set to 10.0",
        )
        args = self._make_args()
        _run_push(args, client)
        client.set_grade.assert_called_once_with(500003, 10.0, comment="")

    def test_grade_with_comment(self) -> None:
        client = MagicMock()
        client.set_grade.return_value = WriteResult(
            success=True,
            action="grade",
            issue_id=500003,
            value="10.0",
        )
        args = self._make_args(comment="Good work")
        _run_push(args, client)
        client.set_grade.assert_called_once_with(500003, 10.0, comment="Good work")

    def test_status_calls_set_status(self) -> None:
        client = MagicMock()
        client.set_status.return_value = WriteResult(
            success=True,
            action="status",
            issue_id=500003,
            value="5",
        )
        args = self._make_args(push_action="status", status="accepted")
        _run_push(args, client)
        client.set_status.assert_called_once_with(500003, 5, comment="")

    def test_comment_calls_add_comment(self) -> None:
        client = MagicMock()
        client.add_comment.return_value = WriteResult(
            success=True,
            action="comment",
            issue_id=500003,
            value="Hello",
        )
        args = self._make_args(push_action="comment", comment="Hello")
        _run_push(args, client)
        client.add_comment.assert_called_once_with(500003, "Hello")

    def test_failed_result_exits(self) -> None:
        client = MagicMock()
        client.set_grade.return_value = WriteResult(
            success=False,
            action="grade",
            issue_id=500003,
            value="99",
            message="exceeds max",
        )
        args = self._make_args(grade=99.0)
        with pytest.raises(SystemExit):
            _run_push(args, client)

    def test_dry_run_grade(self) -> None:
        client = MagicMock()
        from anytask_scraper.models import SubmissionForms

        client.fetch_submission_page.return_value = "<html></html>"
        forms = SubmissionForms(
            csrf_token="tok",
            has_grade_form=True,
            max_score=14.0,
            issue_id=500003,
        )
        args = self._make_args(dry_run=True)
        with patch("anytask_scraper.parser.extract_submission_forms", return_value=forms):
            _run_push(args, client)

        client.set_grade.assert_not_called()
        client.fetch_submission_page.assert_called_once()

    def test_dry_run_status(self) -> None:
        client = MagicMock()
        from anytask_scraper.models import SubmissionForms

        client.fetch_submission_page.return_value = "<html></html>"
        forms = SubmissionForms(
            csrf_token="tok",
            has_status_form=True,
            issue_id=500003,
            status_options=[(3, "На проверке"), (4, "На доработке"), (5, "Зачтено")],
        )
        args = self._make_args(push_action="status", status="review", dry_run=True)
        with patch("anytask_scraper.parser.extract_submission_forms", return_value=forms):
            _run_push(args, client)

        client.set_status.assert_not_called()

    def test_dry_run_comment(self) -> None:
        client = MagicMock()
        from anytask_scraper.models import SubmissionForms

        client.fetch_submission_page.return_value = "<html></html>"
        forms = SubmissionForms(
            csrf_token="tok",
            has_comment_form=True,
            issue_id=500003,
        )
        args = self._make_args(push_action="comment", comment="hi", dry_run=True)
        with patch("anytask_scraper.parser.extract_submission_forms", return_value=forms):
            _run_push(args, client)

        client.add_comment.assert_not_called()
