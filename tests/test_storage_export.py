from __future__ import annotations

import json
from pathlib import Path

from anytask_scraper.models import Comment, QueueEntry, ReviewQueue, Submission
from anytask_scraper.storage import (
    save_queue_csv,
    save_submissions_csv,
    save_submissions_json,
)


def test_save_queue_csv_supports_custom_filename_without_extension(tmp_path: Path) -> None:
    queue = ReviewQueue(
        course_id=1250,
        entries=[
            QueueEntry(
                student_name="Alice",
                student_url="/u/alice",
                task_title="Task 1",
                update_time="01-01-2026",
                mark="10",
                status_color="success",
                status_name="Done",
                responsible_name="Bob",
                responsible_url="/u/bob",
                has_issue_access=True,
                issue_url="/issue/1",
            )
        ],
    )

    path = save_queue_csv(queue, tmp_path, filename="custom_queue")

    assert path.name == "custom_queue.csv"
    assert path.exists()


def test_save_submissions_csv_applies_columns_and_custom_filename(tmp_path: Path) -> None:
    subs = [
        Submission(
            issue_id=7,
            task_title="Task 1",
            student_name="Alice",
            reviewer_name="Bob",
            status="Done",
            grade="10",
            max_score="10",
            comments=[
                Comment(
                    author_name="Bob",
                    author_url="/u/bob",
                    timestamp=None,
                    content_html="",
                )
            ],
        )
    ]

    path = save_submissions_csv(
        subs,
        course_id=1250,
        output_dir=tmp_path,
        columns=["Issue ID", "Task", "Comments"],
        filename="subs_export.csv",
    )

    assert path.name == "subs_export.csv"
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "Issue ID,Task,Comments"
    assert lines[1].startswith("7,Task 1,1")


def test_save_submissions_json_applies_columns(tmp_path: Path) -> None:
    subs = [
        Submission(
            issue_id=7,
            task_title="Task 1",
            student_name="Alice",
            reviewer_name="Bob",
            status="Done",
            grade="10",
            max_score="10",
        )
    ]

    path = save_submissions_json(
        subs,
        course_id=1250,
        output_dir=tmp_path,
        columns=["Issue ID", "Task"],
        filename="submissions_custom",
    )

    assert path.name == "submissions_custom.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["course_id"] == 1250
    assert payload["submissions"][0] == {"issue_id": 7, "task": "Task 1"}
