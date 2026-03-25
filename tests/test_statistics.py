from __future__ import annotations

from pathlib import Path

from anytask_scraper.cli import _build_parser
from anytask_scraper.json_db import QueueJsonDB
from anytask_scraper.models import QueueEntry, ReviewQueue


def _make_entry(
    student_name: str,
    student_url: str,
    task_title: str,
    issue_url: str,
) -> QueueEntry:
    return QueueEntry(
        student_name=student_name,
        student_url=student_url,
        task_title=task_title,
        update_time="2026-02-28 10:00",
        mark="8",
        status_color="warning",
        status_name="On Review",
        responsible_name="Bob",
        responsible_url="/users/bob/",
        has_issue_access=True,
        issue_url=issue_url,
    )


def _seed_db(path: Path) -> None:
    db = QueueJsonDB(path)

    queue_1250 = ReviewQueue(
        course_id=1250,
        entries=[
            _make_entry("Alice Smith", "/users/alice/", "HW 1", "/issue/500001"),
            _make_entry("Carol Jones", "/users/carol/", "HW 2", "/issue/500002"),
        ],
    )
    db.sync_queue(queue_1250, course_title="Python")

    queue_1251 = ReviewQueue(
        course_id=1251,
        entries=[
            _make_entry("Dave Brown", "/users/dave/", "Lab 1", "/issue/500003"),
            _make_entry("Eve White", "/users/eve/", "Lab 2", "/issue/500004"),
        ],
    )
    db.sync_queue(queue_1251, course_title="Algorithms")


def test_statistics_total_counts(tmp_path: Path) -> None:
    db_path = tmp_path / "queue_db.json"
    _seed_db(db_path)

    db = QueueJsonDB(db_path)
    stats = db.statistics()

    assert stats["total"] == 4
    assert stats["new"] == 4
    assert stats["pulled"] == 0
    assert stats["processed"] == 0


def test_statistics_by_course_breakdown(tmp_path: Path) -> None:
    db_path = tmp_path / "queue_db.json"
    _seed_db(db_path)

    db = QueueJsonDB(db_path)
    stats = db.statistics()

    by_course = stats["by_course"]
    assert 1250 in by_course
    assert 1251 in by_course

    assert by_course[1250]["total"] == 2
    assert by_course[1250]["new"] == 2
    assert by_course[1251]["total"] == 2
    assert by_course[1251]["new"] == 2


def test_statistics_pulled_count(tmp_path: Path) -> None:
    db_path = tmp_path / "queue_db.json"
    _seed_db(db_path)

    db = QueueJsonDB(db_path)

    db.pull_new_entries(course_id=1250, limit=1)

    stats = db.statistics()

    assert stats["total"] == 4
    assert stats["pulled"] == 1
    assert stats["new"] == 3


def test_statistics_processed_count(tmp_path: Path) -> None:
    db_path = tmp_path / "queue_db.json"
    _seed_db(db_path)

    db = QueueJsonDB(db_path)

    pulled = db.pull_new_entries(course_id=1251, limit=1)
    assert len(pulled) == 1

    first = pulled[0]
    db.mark_entry_processed(
        course_id=first["course_id"],
        student_key=first["student_key"],
        assignment_key=first["assignment_key"],
    )

    stats = db.statistics()

    assert stats["processed"] == 1
    assert stats["pulled"] == 0
    assert stats["new"] == 3


def test_statistics_course_id_filter(tmp_path: Path) -> None:
    db_path = tmp_path / "queue_db.json"
    _seed_db(db_path)

    db = QueueJsonDB(db_path)
    stats = db.statistics(course_id=1250)

    assert stats["total"] == 2
    assert stats["new"] == 2
    assert stats["pulled"] == 0
    assert stats["processed"] == 0

    assert set(stats["by_course"].keys()) == {1250}


def test_statistics_course_id_filter_other_course(tmp_path: Path) -> None:
    db_path = tmp_path / "queue_db.json"
    _seed_db(db_path)

    db = QueueJsonDB(db_path)
    stats = db.statistics(course_id=1251)

    assert stats["total"] == 2
    assert set(stats["by_course"].keys()) == {1251}


def test_statistics_empty_db(tmp_path: Path) -> None:
    db_path = tmp_path / "queue_db.json"
    db = QueueJsonDB(db_path)

    stats = db.statistics()

    assert stats["total"] == 0
    assert stats["new"] == 0
    assert stats["pulled"] == 0
    assert stats["processed"] == 0
    assert stats["by_course"] == {}


def test_parser_db_diff(tmp_path: Path) -> None:
    parser = _build_parser()
    db_file = str(tmp_path / "queue_db.json")

    args = parser.parse_args(["db", "diff", "--db-file", db_file, "-c", "1250"])

    assert args.command == "db"
    assert args.db_action == "diff"
    assert args.course == 1250
    assert args.db_file == db_file


def test_parser_db_stats(tmp_path: Path) -> None:
    parser = _build_parser()
    db_file = str(tmp_path / "queue_db.json")

    args = parser.parse_args(["db", "stats", "--db-file", db_file])

    assert args.command == "db"
    assert args.db_action == "stats"
    assert args.db_file == db_file


def test_parser_db_stats_with_course(tmp_path: Path) -> None:
    parser = _build_parser()
    db_file = str(tmp_path / "queue_db.json")

    args = parser.parse_args(["db", "stats", "--db-file", db_file, "-c", "1250"])

    assert args.command == "db"
    assert args.db_action == "stats"
    assert args.course == 1250


def test_parser_db_sync_interval(tmp_path: Path) -> None:
    parser = _build_parser()
    db_file = str(tmp_path / "queue_db.json")

    args = parser.parse_args(
        ["db", "sync", "-c", "1250", "--interval", "300", "--db-file", db_file]
    )

    assert args.command == "db"
    assert args.db_action == "sync"
    assert args.course == 1250
    assert args.interval == 300
    assert args.db_file == db_file
