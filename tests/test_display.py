from rich.console import Console

from anytask_scraper.display import display_course, display_task_detail
from anytask_scraper.parser import parse_course_page

from .html_builders import (
    StudentTask,
    TeacherGroup,
    TeacherTask,
    build_student_course_page,
    build_teacher_course_page,
)


def test_display_student_course_no_crash() -> None:
    html = build_student_course_page(
        course_id=9001,
        title="Python для анализа данных",
        tasks=[
            StudentTask(
                task_id=80001,
                title="numpy",
                score="10.3",
                status="Зачтено",
                deadline="00:00 19-01-2025",
            ),
        ],
    )
    course = parse_course_page(html, 9001)
    console = Console(file=None, force_terminal=True)
    display_course(course, console)


def test_display_teacher_course_no_crash() -> None:
    html = build_teacher_course_page(
        course_id=9003,
        title="Python для АД",
        groups=[
            TeacherGroup(
                group_id=2368,
                section_name="Группа 251",
                tasks=[
                    TeacherTask(
                        task_id=80012,
                        title="numpy",
                        edit_url="/task/edit/80012",
                        max_score="13",
                        deadline="00:00 19-01-2026",
                    ),
                ],
            ),
        ],
    )
    course = parse_course_page(html, 9003)
    console = Console(file=None, force_terminal=True)
    display_course(course, console)


def test_display_empty_course_no_crash() -> None:
    from anytask_scraper.models import Course

    course = Course(course_id=9999, title="Empty Course")
    console = Console(file=None, force_terminal=True)
    display_course(course, console)


def test_display_task_detail_no_crash() -> None:
    html = build_student_course_page(
        course_id=9001,
        title="Python",
        tasks=[
            StudentTask(
                task_id=80001,
                title="numpy",
                score="10.3",
                deadline="00:00 19-01-2025",
                description_html="<p>Task description here</p>",
            ),
        ],
    )
    course = parse_course_page(html, 9001)
    console = Console(file=None, force_terminal=True)
    display_task_detail(course.tasks[0], console)
