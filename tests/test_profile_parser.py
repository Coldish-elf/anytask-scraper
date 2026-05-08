from anytask_scraper.parser import parse_profile_page

from .html_builders import build_profile_page


class TestParseProfilePage:
    def setup_method(self) -> None:
        html = build_profile_page(
            teacher_courses=[
                (9002, "ИИ > Прикладной Python 25'"),
                (9003, "ВШЭ > КНАД > Python для АД 26`"),
            ],
            student_courses=[
                (9001, "Python для сбора и анализа данных 24/25"),
                (9002, "ИИ > Прикладной Python 25'"),
                (9004, "ВШЭ > ПМИ > Машинное обучение 1"),
            ],
        )
        self.entries = parse_profile_page(html)
        self.by_id = {e.course_id: e for e in self.entries}

    def test_finds_all_courses(self) -> None:
        assert len(self.entries) == 4

    def test_teacher_courses_detected(self) -> None:
        teacher = [e for e in self.entries if e.role == "teacher"]
        assert len(teacher) == 2
        teacher_ids = {e.course_id for e in teacher}
        assert teacher_ids == {9002, 9003}

    def test_student_courses_detected(self) -> None:
        student = [e for e in self.entries if e.role == "student"]
        assert len(student) == 2
        student_ids = {e.course_id for e in student}
        assert student_ids == {9001, 9004}

    def test_teacher_takes_priority_over_student(self) -> None:
        entry = self.by_id[9002]
        assert entry.role == "teacher"

    def test_course_titles_extracted(self) -> None:
        assert "Python" in self.by_id[9002].title
        assert self.by_id[9003].title != ""
        assert self.by_id[9001].title != ""
        assert self.by_id[9004].title != ""

    def test_student_only_filtering(self) -> None:
        teacher_ids = {e.course_id for e in self.entries if e.role == "teacher"}
        student_only = [
            e for e in self.entries if e.role == "student" and e.course_id not in teacher_ids
        ]
        assert len(student_only) == 2
        student_only_ids = {e.course_id for e in student_only}
        assert student_only_ids == {9001, 9004}


class TestParseProfilePageEmpty:
    def test_empty_html(self) -> None:
        assert parse_profile_page("") == []

    def test_no_courses_section(self) -> None:
        assert parse_profile_page("<html><body></body></html>") == []

    def test_teacher_only(self) -> None:
        html = """
        <div id="teacher_course">
            <li class="list-group-item"><a href="/course/100">Course A</a></li>
        </div>
        """
        entries = parse_profile_page(html)
        assert len(entries) == 1
        assert entries[0].course_id == 100
        assert entries[0].role == "teacher"

    def test_student_only(self) -> None:
        html = """
        <div id="course_list">
            <li class="list-group-item"><a href="/course/200">Course B</a></li>
        </div>
        """
        entries = parse_profile_page(html)
        assert len(entries) == 1
        assert entries[0].course_id == 200
        assert entries[0].role == "student"

    def test_plural_course_url_and_container_variants(self) -> None:
        html = """
        <section id="teacher_courses">
            <a href="/courses/100">Course A</a>
        </section>
        <section id="student_courses">
            <a href="/courses/200">Course B</a>
            <a href="/courses/100">Course A</a>
        </section>
        """
        entries = parse_profile_page(html)
        by_id = {entry.course_id: entry for entry in entries}

        assert by_id[100].role == "teacher"
        assert by_id[200].role == "student"
