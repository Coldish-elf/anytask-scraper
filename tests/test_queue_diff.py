from __future__ import annotations

from pathlib import Path

import pytest

from anytask_scraper.cli import _build_parser
from anytask_scraper.json_db import QueueJsonDB
from anytask_scraper.models import QueueEntry, ReviewQueue


def _make_entry(
    *,
    student_name: str = "Alice Smith",
    student_url: str = "/users/alice/",
    task_title: str = "HW 1",
    update_time: str = "2026-02-28 10:00",
    mark: str = "8",
    status_color: str = "warning",
    status_name: str = "On Review",
    responsible_name: str = "Bob",
    responsible_url: str = "/users/bob/",
    has_issue_access: bool = True,
    issue_url: str = "/issue/421525",
) -> QueueEntry:
    return QueueEntry(
        student_name=student_name,
        student_url=student_url,
        task_title=task_title,
        update_time=update_time,
        mark=mark,
        status_color=status_color,
        status_name=status_name,
        responsible_name=responsible_name,
        responsible_url=responsible_url,
        has_issue_access=has_issue_access,
        issue_url=issue_url,
    )


def _make_queue(course_id: int = 1250, entries: list[QueueEntry] | None = None) -> ReviewQueue:
    return ReviewQueue(
        course_id=course_id,
        entries=entries if entries is not None else [_make_entry()],
    )


def _seed_db(path: Path, course_id: int = 1250) -> QueueJsonDB:
    db = QueueJsonDB(path, autosave=True)
    db.sync_queue(_make_queue(course_id=course_id), course_title="Python")
    return db


def test_diff_assignment_no_prior_snapshot(tmp_path: Path) -> None:
    db_path = tmp_path / "queue_db.json"
    db = _seed_db(db_path)

    diffs = db.diff_assignment(
        course_id=1250,
        student_key="/users/alice/",
        assignment_key="issue:421525",
    )
    assert diffs == []


def test_diff_assignment_no_changes(tmp_path: Path) -> None:
    db_path = tmp_path / "queue_db.json"
    db = _seed_db(db_path)

    db.sync_queue(_make_queue(), course_title="Python")

    diffs = db.diff_assignment(
        course_id=1250,
        student_key="/users/alice/",
        assignment_key="issue:421525",
    )
    assert diffs == []


def test_diff_assignment_status_changed(tmp_path: Path) -> None:
    db_path = tmp_path / "queue_db.json"
    db = _seed_db(db_path)

    changed_entry = _make_entry(status_name="Accepted", update_time="2026-02-28 12:00")
    db.sync_queue(_make_queue(entries=[changed_entry]), course_title="Python")

    diffs = db.diff_assignment(
        course_id=1250,
        student_key="/users/alice/",
        assignment_key="issue:421525",
    )
    assert len(diffs) >= 1
    status_diff = next((d for d in diffs if d["field"] == "status"), None)
    assert status_diff is not None
    assert status_diff["old"] == "On Review"
    assert status_diff["new"] == "Accepted"


def test_diff_assignment_grade_changed(tmp_path: Path) -> None:
    db_path = tmp_path / "queue_db.json"
    db = _seed_db(db_path)

    changed_entry = _make_entry(mark="10", update_time="2026-02-28 12:00")
    db.sync_queue(_make_queue(entries=[changed_entry]), course_title="Python")

    diffs = db.diff_assignment(
        course_id=1250,
        student_key="/users/alice/",
        assignment_key="issue:421525",
    )
    grade_diff = next((d for d in diffs if d["field"] == "grade"), None)
    assert grade_diff is not None
    assert grade_diff["old"] == "8"
    assert grade_diff["new"] == "10"


def test_diff_assignment_reviewer_changed(tmp_path: Path) -> None:
    db_path = tmp_path / "queue_db.json"
    db = _seed_db(db_path)

    changed_entry = _make_entry(responsible_name="Carol", update_time="2026-02-28 13:00")
    db.sync_queue(_make_queue(entries=[changed_entry]), course_title="Python")

    diffs = db.diff_assignment(
        course_id=1250,
        student_key="/users/alice/",
        assignment_key="issue:421525",
    )
    reviewer_diff = next((d for d in diffs if d["field"] == "reviewer"), None)
    assert reviewer_diff is not None
    assert reviewer_diff["old"] == "Bob"
    assert reviewer_diff["new"] == "Carol"


def test_diff_assignment_multiple_fields_changed(tmp_path: Path) -> None:
    db_path = tmp_path / "queue_db.json"
    db = _seed_db(db_path)

    changed_entry = _make_entry(
        status_name="Accepted",
        mark="10",
        responsible_name="Carol",
        update_time="2026-02-28 14:00",
    )
    db.sync_queue(_make_queue(entries=[changed_entry]), course_title="Python")

    diffs = db.diff_assignment(
        course_id=1250,
        student_key="/users/alice/",
        assignment_key="issue:421525",
    )
    fields = {d["field"] for d in diffs}
    assert "status" in fields
    assert "grade" in fields
    assert "reviewer" in fields

    for d in diffs:
        assert set(d.keys()) == {"field", "old", "new"}


def test_diff_assignment_only_updated_time_changed(tmp_path: Path) -> None:
    db_path = tmp_path / "queue_db.json"
    db = _seed_db(db_path)

    changed_entry = _make_entry(update_time="2026-03-01 09:00")
    db.sync_queue(_make_queue(entries=[changed_entry]), course_title="Python")

    diffs = db.diff_assignment(
        course_id=1250,
        student_key="/users/alice/",
        assignment_key="issue:421525",
    )
    updated_diff = next((d for d in diffs if d["field"] == "updated"), None)
    assert updated_diff is not None
    assert updated_diff["old"] == "2026-02-28 10:00"
    assert updated_diff["new"] == "2026-03-01 09:00"


def test_diff_assignment_uses_last_two_snapshots(tmp_path: Path) -> None:
    db_path = tmp_path / "queue_db.json"
    db = _seed_db(db_path)

    intermediate = _make_entry(status_name="Needs Fix", update_time="2026-02-28 11:00")
    db.sync_queue(_make_queue(entries=[intermediate]), course_title="Python")

    final = _make_entry(status_name="Accepted", update_time="2026-02-28 15:00")
    db.sync_queue(_make_queue(entries=[final]), course_title="Python")

    diffs = db.diff_assignment(
        course_id=1250,
        student_key="/users/alice/",
        assignment_key="issue:421525",
    )
    status_diff = next((d for d in diffs if d["field"] == "status"), None)
    assert status_diff is not None

    assert status_diff["old"] == "Needs Fix"
    assert status_diff["new"] == "Accepted"


def test_diff_assignment_unknown_course(tmp_path: Path) -> None:
    db_path = tmp_path / "queue_db.json"
    db = _seed_db(db_path)

    diffs = db.diff_assignment(
        course_id=9999,
        student_key="/users/alice/",
        assignment_key="issue:421525",
    )
    assert diffs == []


def test_diff_assignment_unknown_student(tmp_path: Path) -> None:
    db_path = tmp_path / "queue_db.json"
    db = _seed_db(db_path)

    diffs = db.diff_assignment(
        course_id=1250,
        student_key="/users/nobody/",
        assignment_key="issue:421525",
    )
    assert diffs == []


def test_diff_assignment_unknown_assignment(tmp_path: Path) -> None:
    db_path = tmp_path / "queue_db.json"
    db = _seed_db(db_path)

    diffs = db.diff_assignment(
        course_id=1250,
        student_key="/users/alice/",
        assignment_key="issue:999999",
    )
    assert diffs == []


def test_get_changed_entries_empty_after_single_sync(tmp_path: Path) -> None:
    db_path = tmp_path / "queue_db.json"
    db = _seed_db(db_path)

    changed = db.get_changed_entries()
    assert changed == []


def test_get_changed_entries_returns_changed_entry(tmp_path: Path) -> None:
    db_path = tmp_path / "queue_db.json"
    db = _seed_db(db_path)

    changed_entry = _make_entry(status_name="Accepted", update_time="2026-02-28 12:00")
    db.sync_queue(_make_queue(entries=[changed_entry]), course_title="Python")

    changed = db.get_changed_entries()
    assert len(changed) == 1
    item = changed[0]
    assert item["course_id"] == 1250
    assert item["student_key"] == "/users/alice/"
    assert item["assignment_key"] == "issue:421525"
    assert item["student_name"] == "Alice Smith"
    assert item["task_title"] == "HW 1"
    assert item["issue_id"] == 421525
    assert isinstance(item["diffs"], list)
    assert len(item["diffs"]) >= 1
    assert "current_status" in item


def test_get_changed_entries_unchanged_not_included(tmp_path: Path) -> None:
    db_path = tmp_path / "queue_db.json"
    db = _seed_db(db_path)

    db.sync_queue(_make_queue(), course_title="Python")

    changed = db.get_changed_entries()
    assert changed == []


def test_get_changed_entries_diffs_populated(tmp_path: Path) -> None:
    db_path = tmp_path / "queue_db.json"
    db = _seed_db(db_path)

    changed_entry = _make_entry(mark="10", update_time="2026-02-28 12:00")
    db.sync_queue(_make_queue(entries=[changed_entry]), course_title="Python")

    changed = db.get_changed_entries()
    assert len(changed) == 1
    diffs = changed[0]["diffs"]
    assert len(diffs) >= 1
    for d in diffs:
        assert {"field", "old", "new"} <= set(d.keys())


def test_get_changed_entries_current_status_is_latest(tmp_path: Path) -> None:
    db_path = tmp_path / "queue_db.json"
    db = _seed_db(db_path)

    changed_entry = _make_entry(status_name="Accepted", update_time="2026-02-28 12:00")
    db.sync_queue(_make_queue(entries=[changed_entry]), course_title="Python")

    changed = db.get_changed_entries()
    assert changed[0]["current_status"] == "Accepted"


def test_get_changed_entries_course_id_filter(tmp_path: Path) -> None:
    db_path = tmp_path / "queue_db.json"
    db = QueueJsonDB(db_path, autosave=True)

    entry_a = _make_entry(issue_url="/issue/100")
    entry_b = _make_entry(
        student_name="Bob Jones",
        student_url="/users/bob/",
        task_title="HW 2",
        issue_url="/issue/200",
    )
    db.sync_queue(_make_queue(course_id=1250, entries=[entry_a]), course_title="Course A")
    db.sync_queue(_make_queue(course_id=1300, entries=[entry_b]), course_title="Course B")

    changed_a = _make_entry(
        status_name="Accepted", update_time="2026-03-01 09:00", issue_url="/issue/100"
    )
    changed_b = _make_entry(
        student_name="Bob Jones",
        student_url="/users/bob/",
        task_title="HW 2",
        issue_url="/issue/200",
        status_name="Accepted",
        update_time="2026-03-01 09:00",
    )
    db.sync_queue(_make_queue(course_id=1250, entries=[changed_a]), course_title="Course A")
    db.sync_queue(_make_queue(course_id=1300, entries=[changed_b]), course_title="Course B")

    changed_all = db.get_changed_entries()
    assert len(changed_all) == 2

    changed_1250 = db.get_changed_entries(course_id=1250)
    assert len(changed_1250) == 1
    assert changed_1250[0]["course_id"] == 1250

    changed_1300 = db.get_changed_entries(course_id=1300)
    assert len(changed_1300) == 1
    assert changed_1300[0]["course_id"] == 1300


def test_statistics_initial_all_new(tmp_path: Path) -> None:
    db_path = tmp_path / "queue_db.json"
    db = _seed_db(db_path)

    stats = db.statistics()
    assert stats["total"] == 1
    assert stats["new"] == 1
    assert stats["pulled"] == 0
    assert stats["processed"] == 0
    assert "by_course" in stats


def test_statistics_by_course_initial(tmp_path: Path) -> None:
    db_path = tmp_path / "queue_db.json"
    db = _seed_db(db_path)

    stats = db.statistics()
    assert 1250 in stats["by_course"]
    course_stats = stats["by_course"][1250]
    assert course_stats["total"] == 1
    assert course_stats["new"] == 1
    assert course_stats["pulled"] == 0
    assert course_stats["processed"] == 0


def test_statistics_after_pull(tmp_path: Path) -> None:
    db_path = tmp_path / "queue_db.json"
    db = _seed_db(db_path)

    db.pull_new_entries(course_id=1250)

    stats = db.statistics()
    assert stats["total"] == 1
    assert stats["new"] == 0
    assert stats["pulled"] == 1
    assert stats["processed"] == 0


def test_statistics_after_process(tmp_path: Path) -> None:
    db_path = tmp_path / "queue_db.json"
    db = _seed_db(db_path)

    db.pull_new_entries(course_id=1250)
    db.mark_entry_processed(
        course_id=1250,
        student_key="/users/alice/",
        assignment_key="issue:421525",
    )

    stats = db.statistics()
    assert stats["total"] == 1
    assert stats["new"] == 0
    assert stats["pulled"] == 0
    assert stats["processed"] == 1


def test_statistics_course_id_filter(tmp_path: Path) -> None:
    db_path = tmp_path / "queue_db.json"
    db = QueueJsonDB(db_path, autosave=True)

    entry_b = _make_entry(
        student_name="Bob Jones",
        student_url="/users/bob/",
        task_title="HW 2",
        issue_url="/issue/200",
    )
    db.sync_queue(_make_queue(course_id=1250), course_title="Course A")
    db.sync_queue(_make_queue(course_id=1300, entries=[entry_b]), course_title="Course B")

    stats_1250 = db.statistics(course_id=1250)
    assert stats_1250["total"] == 1
    assert 1300 not in stats_1250["by_course"]

    stats_1300 = db.statistics(course_id=1300)
    assert stats_1300["total"] == 1
    assert 1250 not in stats_1300["by_course"]


def test_statistics_multiple_entries_multiple_courses(tmp_path: Path) -> None:
    db_path = tmp_path / "queue_db.json"
    db = QueueJsonDB(db_path, autosave=True)

    entry_alice = _make_entry()
    entry_bob = _make_entry(
        student_name="Bob Jones",
        student_url="/users/bob/",
        task_title="HW 2",
        issue_url="/issue/200",
    )
    entry_carol = _make_entry(
        student_name="Carol White",
        student_url="/users/carol/",
        task_title="HW 3",
        issue_url="/issue/300",
    )

    db.sync_queue(_make_queue(course_id=1250, entries=[entry_alice, entry_bob]))
    db.sync_queue(_make_queue(course_id=1300, entries=[entry_carol]))

    db.pull_new_entries(course_id=1250, limit=1)

    stats = db.statistics()
    assert stats["total"] == 3
    assert stats["pulled"] == 1
    assert stats["new"] == 2

    by_1250 = stats["by_course"][1250]
    by_1300 = stats["by_course"][1300]
    assert by_1250["total"] == 2
    assert by_1300["total"] == 1


def test_statistics_empty_db(tmp_path: Path) -> None:
    db_path = tmp_path / "queue_db.json"
    db = QueueJsonDB(db_path, autosave=True)

    stats = db.statistics()
    assert stats["total"] == 0
    assert stats["new"] == 0
    assert stats["pulled"] == 0
    assert stats["processed"] == 0
    assert stats["by_course"] == {}


def test_parser_db_diff_course_filter() -> None:
    parser = _build_parser()

    args = parser.parse_args(["db", "diff", "--db-file", "queue_db.json", "--course", "1250"])
    assert args.command == "db"
    assert args.db_action == "diff"
    assert args.db_file == "queue_db.json"
    assert args.course == 1250


def test_parser_db_diff_defaults() -> None:
    parser = _build_parser()

    args = parser.parse_args(["db", "diff"])
    assert args.command == "db"
    assert args.db_action == "diff"
    assert args.course is None
    assert args.format == "table"


def test_parser_db_diff_format_json() -> None:
    parser = _build_parser()

    args = parser.parse_args(["db", "diff", "--format", "json"])
    assert args.format == "json"


def test_parser_db_diff_format_table() -> None:
    parser = _build_parser()

    args = parser.parse_args(["db", "diff", "-f", "table"])
    assert args.format == "table"


def test_parser_db_stats_defaults() -> None:
    parser = _build_parser()

    args = parser.parse_args(["db", "stats", "--db-file", "queue_db.json"])
    assert args.command == "db"
    assert args.db_action == "stats"
    assert args.db_file == "queue_db.json"
    assert args.course is None


def test_parser_db_stats_with_course() -> None:
    parser = _build_parser()

    args = parser.parse_args(["db", "stats", "-c", "1250"])
    assert args.course == 1250


def test_parser_db_sync_interval() -> None:
    parser = _build_parser()

    args = parser.parse_args(["db", "sync", "--course", "1250", "--interval", "300"])
    assert args.command == "db"
    assert args.db_action == "sync"
    assert args.interval == 300
    assert isinstance(args.interval, int)


def test_parser_db_sync_interval_default_is_none() -> None:
    parser = _build_parser()

    args = parser.parse_args(["db", "sync", "--course", "1250"])
    assert args.interval is None


def test_parser_db_sync_required_course() -> None:
    parser = _build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(["db", "sync"])
