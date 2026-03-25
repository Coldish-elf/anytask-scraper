from datetime import datetime
from pathlib import Path

from anytask_scraper.parser import format_student_folder, parse_course_page, strip_html

from .html_builders import (
    StudentTask,
    TeacherGroup,
    TeacherTask,
    build_student_course_page,
    build_teacher_course_page,
)


class TestStudentPython9001:
    def setup_method(self) -> None:
        tasks = [
            StudentTask(
                task_id=80001,
                title="numpy",
                score="10.3",
                status="Зачтено",
                status_color="#65E31B",
                deadline="00:00 19-01-2025",
                submit_url="/issue/get_or_create/80001/300042",
                description_html=(
                    '<p><a href="https://colab.research.google.com/drive/1xG9SK">'
                    "https://colab.research.google.com/drive/1xG9SK</a></p>"
                ),
            ),
            StudentTask(
                task_id=80002,
                title="pandas",
                score="10.0",
                status="Зачтено",
                status_color="#65E31B",
                deadline="00:00 25-01-2025",
                submit_url="/issue/get_or_create/80002/300042",
            ),
            StudentTask(
                task_id=80003,
                title="join",
                score="11.25",
                status="Зачтено",
                deadline="00:00 01-02-2025",
                submit_url="/issue/get_or_create/80003/300042",
            ),
            StudentTask(
                task_id=80004,
                title="matplotlib",
                score="7.0",
                status="Зачтено",
                deadline="00:00 08-02-2025",
            ),
            StudentTask(
                task_id=80005,
                title="seaborn",
                score="5.0",
                status="Зачтено",
                deadline="00:00 15-02-2025",
            ),
            StudentTask(
                task_id=80006,
                title="requests",
                score="10.0",
                status="Зачтено",
                deadline="00:00 22-02-2025",
            ),
            StudentTask(
                task_id=80007,
                title="selenium",
                score="8.0",
                status="Зачтено",
                deadline="00:00 01-03-2025",
            ),
            StudentTask(
                task_id=80008,
                title="flask",
                score="9.0",
                status="Зачтено",
                deadline="00:00 08-03-2025",
            ),
            StudentTask(
                task_id=80009,
                title="final",
                score="0.0",
                status="Новый",
                deadline="00:00 15-03-2025",
            ),
        ]
        html = build_student_course_page(
            course_id=9001,
            title="Python для сбора и анализа данных 24/25",
            teachers=["Пончикова Марина", "Кактусов Аркадий", "Тапочкин Василий"],
            tasks=tasks,
        )
        self.course = parse_course_page(html, 9001)

    def test_course_title(self) -> None:
        assert "Python" in self.course.title or "python" in self.course.title.lower()

    def test_course_id(self) -> None:
        assert self.course.course_id == 9001

    def test_teachers_extracted(self) -> None:
        assert len(self.course.teachers) > 0

    def test_tasks_found(self) -> None:
        assert len(self.course.tasks) >= 9

    def test_first_task_title(self) -> None:
        assert self.course.tasks[0].title == "numpy"

    def test_first_task_id(self) -> None:
        assert self.course.tasks[0].task_id == 80001

    def test_first_task_score(self) -> None:
        assert self.course.tasks[0].score == 10.3

    def test_first_task_status(self) -> None:
        assert self.course.tasks[0].status == "Зачтено"

    def test_first_task_submit_url(self) -> None:
        assert self.course.tasks[0].submit_url == "/issue/get_or_create/80001/300042"

    def test_first_task_deadline(self) -> None:
        assert self.course.tasks[0].deadline == datetime(2025, 1, 19, 0, 0)

    def test_first_task_description(self) -> None:
        assert (
            "colab.research.google.com" in self.course.tasks[0].description
            or "google.com" in self.course.tasks[0].description
        )

    def test_second_task_title(self) -> None:
        assert self.course.tasks[1].title == "pandas"

    def test_new_task_status(self) -> None:
        new_tasks = [t for t in self.course.tasks if t.status == "Новый"]
        if new_tasks:
            assert new_tasks[0].score == 0.0


class TestStudentML9004:
    def setup_method(self) -> None:
        tasks = [
            StudentTask(
                task_id=90001,
                title="homework-practice-01-tabular",
                score="0.0",
                deadline="00:00 15-03-2026",
            ),
        ]
        html = build_student_course_page(
            course_id=9004,
            title="Машинное обучение",
            teachers=["Печенькин Гриша"],
            tasks=tasks,
        )
        self.course = parse_course_page(html, 9004)

    def test_course_id(self) -> None:
        assert self.course.course_id == 9004

    def test_tasks_found(self) -> None:
        assert len(self.course.tasks) >= 1

    def test_task_has_deadline(self) -> None:
        assert self.course.tasks[0].deadline is not None


class TestTeacherPython9002:
    def setup_method(self) -> None:
        groups = [
            TeacherGroup(
                group_id=2340,
                section_name="ИИ > Прикладной Python 25'",
                tasks=[
                    TeacherTask(
                        task_id=80010,
                        title="Streamlit. Первый проект",
                        edit_url="/task/edit/80010",
                        max_score="12",
                        deadline="00:00 22-12-2025",
                    ),
                    TeacherTask(
                        task_id=80011,
                        title="Телеграм-бот. Второй проект",
                        edit_url="/task/edit/80011",
                        max_score="14",
                        deadline="00:00 17-01-2026",
                    ),
                ],
            ),
        ]
        html = build_teacher_course_page(
            course_id=9002,
            title="Прикладной Python 25'",
            teachers=["Бублик Сергей"],
            groups=groups,
        )
        self.course = parse_course_page(html, 9002)

    def test_course_id(self) -> None:
        assert self.course.course_id == 9002

    def test_teachers_extracted(self) -> None:
        assert len(self.course.teachers) > 0

    def test_tasks_found(self) -> None:
        assert len(self.course.tasks) >= 2

    def test_tasks_have_section(self) -> None:
        for task in self.course.tasks:
            assert task.section != ""

    def test_task_has_edit_url(self) -> None:
        assert self.course.tasks[0].edit_url.startswith("/task/edit/")

    def test_task_has_max_score(self) -> None:
        assert self.course.tasks[0].max_score is not None
        assert self.course.tasks[0].max_score > 0

    def test_task_has_deadline(self) -> None:
        assert self.course.tasks[0].deadline is not None

    def test_first_task_title(self) -> None:
        assert "Streamlit" in self.course.tasks[0].title or "проект" in self.course.tasks[0].title


class TestTeacherPython9003:
    def setup_method(self) -> None:
        groups = [
            TeacherGroup(
                group_id=2368,
                section_name="Python для АД 26` (251)",
                tasks=[
                    TeacherTask(
                        task_id=80012,
                        title="numpy",
                        edit_url="/task/edit/80012",
                        max_score="13",
                        deadline="00:00 19-01-2026",
                    ),
                    TeacherTask(
                        task_id=80013,
                        title="pandas",
                        edit_url="/task/edit/80013",
                        max_score="13",
                        deadline="00:00 25-01-2026",
                    ),
                ],
            ),
            TeacherGroup(
                group_id=2369,
                section_name="Python для АД 26` (252)",
                tasks=[
                    TeacherTask(
                        task_id=80014,
                        title="join",
                        edit_url="/task/edit/80014",
                        max_score="13",
                        deadline="00:00 01-02-2026",
                    ),
                ],
            ),
        ]
        html = build_teacher_course_page(
            course_id=9003,
            title="Python для АД 26`",
            teachers=["Ёжикова Надежда"],
            groups=groups,
        )
        self.course = parse_course_page(html, 9003)

    def test_course_id(self) -> None:
        assert self.course.course_id == 9003

    def test_multiple_groups(self) -> None:
        sections = {t.section for t in self.course.tasks}
        assert len(sections) >= 2, f"Expected multiple groups, got: {sections}"

    def test_tasks_found(self) -> None:
        assert len(self.course.tasks) >= 3

    def test_tasks_have_sections(self) -> None:
        for task in self.course.tasks:
            assert task.section != ""


def test_save_course_json(tmp_path: Path) -> None:
    import json

    from anytask_scraper.storage import save_course_json

    tasks = [
        StudentTask(
            task_id=80000 + i,
            title=f"task_{i}",
            score=str(float(i)),
            deadline=f"00:00 {10 + i:02d}-01-2025",
        )
        for i in range(9)
    ]
    html = build_student_course_page(
        course_id=9001,
        title="Python",
        tasks=tasks,
    )
    course = parse_course_page(html, 9001)
    path = save_course_json(course, tmp_path)

    assert path.exists()
    data = json.loads(path.read_text())
    assert data["course_id"] == 9001
    assert len(data["tasks"]) >= 9


class TestStripHtml:
    def test_removes_tags(self) -> None:
        assert strip_html("<p>hello <b>world</b></p>") == "hello world"

    def test_decodes_entities(self) -> None:
        assert strip_html("&amp; &lt;b&gt;") == "& <b>"

    def test_empty_string(self) -> None:
        assert strip_html("") == ""

    def test_plain_text_passthrough(self) -> None:
        assert strip_html("just plain text") == "just plain text"

    def test_nested_html(self) -> None:
        result = strip_html("<div><p>one</p><p>two</p></div>")
        assert "one" in result
        assert "two" in result

    def test_preserves_paragraph_breaks(self) -> None:
        result = strip_html("<p>first paragraph</p><p>second paragraph</p>")
        assert result == "first paragraph\nsecond paragraph"

    def test_preserves_list_item_breaks(self) -> None:
        result = strip_html("<ul><li>item one</li><li>item two</li></ul>")
        assert result == "item one\nitem two"

    def test_br_becomes_newline(self) -> None:
        result = strip_html("line one<br>line two")
        assert result == "line one\nline two"


def test_save_course_markdown(tmp_path: Path) -> None:
    from anytask_scraper.storage import save_course_markdown

    tasks = [
        StudentTask(task_id=80001, title="numpy", score="10.3", deadline="00:00 19-01-2025"),
    ]
    html = build_student_course_page(
        course_id=9001,
        title="Python для сбора данных",
        tasks=tasks,
    )
    course = parse_course_page(html, 9001)
    path = save_course_markdown(course, tmp_path)

    assert path.exists()
    content = path.read_text()
    assert course.title in content
    assert "numpy" in content


class TestFormatStudentFolder:
    def test_normal_name(self) -> None:
        assert format_student_folder("Иванов Иван") == "Иванов_Иван"

    def test_name_with_slash(self) -> None:
        assert format_student_folder("Иванов / Петров") == "Иванов_Петров"

    def test_name_with_backslash(self) -> None:
        assert format_student_folder("Иванов \\ Петров") == "Иванов_Петров"

    def test_name_with_quotes(self) -> None:
        result = format_student_folder('John "Johnny" Doe')
        assert "/" not in result
        assert '"' not in result
        assert result == "John_Johnny_Doe"

    def test_name_with_angle_brackets(self) -> None:
        result = format_student_folder("user<script>")
        assert "<" not in result
        assert ">" not in result

    def test_empty_after_strip(self) -> None:
        assert format_student_folder("   ") == "unknown"

    def test_only_dots(self) -> None:
        assert format_student_folder("...") == "unknown"

    def test_preserves_cyrillic(self) -> None:
        assert format_student_folder("Петров Пётр") == "Петров_Пётр"

    def test_multiple_spaces(self) -> None:
        result = format_student_folder("John   Doe")
        assert result == "John_Doe"

    def test_pipe_and_question_mark(self) -> None:
        result = format_student_folder("test|name?")
        assert "|" not in result
        assert "?" not in result
