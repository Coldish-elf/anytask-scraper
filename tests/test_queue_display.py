from rich.console import Console

from anytask_scraper.display import display_queue, display_submission
from anytask_scraper.models import QueueEntry, ReviewQueue
from anytask_scraper.parser import parse_submission_page

from .html_builders import (
    SubmissionComment,
    SubmissionFile,
    build_submission_page,
)


def test_display_queue_no_crash() -> None:
    entries = [
        QueueEntry(
            student_name="Котлетов Борис",
            student_url="/users/kotletov/",
            task_title="Numpy",
            update_time="06 Фев 12:00",
            mark="5",
            status_color="success",
            status_name="Зачтено",
            responsible_name="Блинчиков Игорь",
            responsible_url="/users/blinchikov/",
            has_issue_access=True,
            issue_url="/issue/12345",
        ),
    ]
    queue = ReviewQueue(course_id=1250, entries=entries)
    console = Console(file=None, force_terminal=True)
    display_queue(queue, console)


def test_display_empty_queue_no_crash() -> None:
    queue = ReviewQueue(course_id=9999)
    console = Console(file=None, force_terminal=True)
    display_queue(queue, console)


def test_display_submission_no_crash() -> None:
    html = build_submission_page(
        issue_id=500001,
        task_title="Join",
        student_name="Кактусов Аркадий",
        student_url="/users/kaktusov/",
        reviewer_name="Сырникова Ольга",
        reviewer_url="/users/syrnikova/",
        status="На проверке",
        grade="0",
        max_score="13",
        deadline="09-02-2026",
        comments=[
            SubmissionComment(
                author_name="Кактусов Аркадий",
                author_url="/users/kaktusov/",
                timestamp="06 Фев 12:00",
                files=[
                    SubmissionFile(
                        filename="hw3.ipynb",
                        download_url="/media/files/hw3.ipynb",
                        is_notebook=True,
                    ),
                ],
            ),
        ],
    )
    sub = parse_submission_page(html, 500001)
    console = Console(file=None, force_terminal=True)
    display_submission(sub, console)


def test_display_submission_after_deadline_no_crash() -> None:
    html = build_submission_page(
        issue_id=500004,
        task_title="Телеграм-бот",
        student_name="Тапочкин Василий",
        student_url="/users/tapochkin/",
        deadline="17-01-2026",
        comments=[
            SubmissionComment(
                author_name="Тапочкин Василий",
                author_url="/users/tapochkin/",
                timestamp="15 Янв 10:00",
                is_after_deadline=True,
                content_html="Поздняя сдача",
            ),
        ],
    )
    sub = parse_submission_page(html, 500004)
    console = Console(file=None, force_terminal=True)
    display_submission(sub, console)
