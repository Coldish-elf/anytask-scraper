from anytask_scraper.parser import parse_gradebook_page

from .html_builders import GradebookGroupData, GradebookStudentRow, build_gradebook_page


class TestGradebookGrouped9003:
    def setup_method(self) -> None:
        html = build_gradebook_page(
            course_id=9003,
            groups=[
                GradebookGroupData(
                    group_id=2368,
                    group_name="Python для АД 26` (251)",
                    teacher_name="Печенькин Гриша",
                    task_titles=["numpy", "pandas", "join", "matplotlib"],
                    max_scores={"numpy": 13.0, "pandas": 13.0, "join": 13.0, "matplotlib": 13.0},
                    entries=[
                        GradebookStudentRow(
                            student_name="Бублик Сергей",
                            student_url="/users/bublik/",
                            scores={"numpy": 0.0, "pandas": 5.0, "join": 8.0, "matplotlib": 0.0},
                            statuses={
                                "numpy": "#65E31B",
                                "pandas": "#65E31B",
                                "join": "#65E31B",
                                "matplotlib": "#ccc",
                            },
                            issue_urls={
                                "numpy": "/issue/get_or_create/80012/300242",
                                "pandas": "/issue/get_or_create/80013/300242",
                                "join": "/issue/get_or_create/80015/300242",
                            },
                            total_score=13.0,
                        ),
                        GradebookStudentRow(
                            student_name="Шпротина Алина",
                            student_url="/users/shprotina/",
                            scores={"numpy": 10.0, "pandas": 12.0},
                            statuses={"numpy": "#65E31B", "pandas": "#65E31B"},
                            issue_urls={"numpy": "/issue/get_or_create/80012/300243"},
                            total_score=22.0,
                        ),
                    ],
                ),
                GradebookGroupData(
                    group_id=2369,
                    group_name="Python для АД 26` (252)",
                    teacher_name="Кефиров Дмитрий",
                    task_titles=["numpy", "pandas", "join", "matplotlib"],
                    max_scores={"numpy": 13.0, "pandas": 13.0, "join": 13.0, "matplotlib": 13.0},
                    entries=[
                        GradebookStudentRow(
                            student_name="Broccoli McStuffins",
                            student_url="/users/broccoli/",
                            scores={"numpy": 8.8},
                            statuses={"numpy": "#65E31B"},
                            issue_urls={"numpy": "/issue/get_or_create/80012/300209"},
                            total_score=8.8,
                        ),
                    ],
                ),
                GradebookGroupData(
                    group_id=2370,
                    group_name="Python для АД 26` (253)",
                    teacher_name="Ёжикова Надежда",
                    task_titles=["numpy", "pandas"],
                    max_scores={"numpy": 13.0, "pandas": 13.0},
                    entries=[
                        GradebookStudentRow(
                            student_name="Тапочкин Василий",
                            student_url="/users/tapochkin/",
                            scores={"numpy": 7.0},
                            statuses={"numpy": "#FF9900"},
                            issue_urls={"numpy": "/issue/get_or_create/80012/300300"},
                            total_score=7.0,
                        ),
                    ],
                ),
            ],
        )
        self.gradebook = parse_gradebook_page(html, 9003)

    def test_course_id(self) -> None:
        assert self.gradebook.course_id == 9003

    def test_groups_found(self) -> None:
        assert len(self.gradebook.groups) >= 3

    def test_first_group_has_name(self) -> None:
        assert self.gradebook.groups[0].group_name

    def test_first_group_has_teacher(self) -> None:
        assert self.gradebook.groups[0].teacher_name

    def test_first_group_has_id(self) -> None:
        assert self.gradebook.groups[0].group_id > 0

    def test_first_group_has_tasks(self) -> None:
        assert len(self.gradebook.groups[0].task_titles) > 0

    def test_first_group_has_entries(self) -> None:
        assert len(self.gradebook.groups[0].entries) > 0

    def test_first_entry_has_student_name(self) -> None:
        entry = self.gradebook.groups[0].entries[0]
        assert entry.student_name

    def test_first_entry_has_student_url(self) -> None:
        entry = self.gradebook.groups[0].entries[0]
        assert entry.student_url.startswith("/users/")

    def test_first_entry_has_scores(self) -> None:
        entry = self.gradebook.groups[0].entries[0]
        assert len(entry.scores) > 0

    def test_first_entry_scores_are_numeric(self) -> None:
        entry = self.gradebook.groups[0].entries[0]
        for val in entry.scores.values():
            assert isinstance(val, float)

    def test_first_entry_has_statuses(self) -> None:
        entry = self.gradebook.groups[0].entries[0]
        assert len(entry.statuses) > 0

    def test_statuses_are_hex_colors(self) -> None:
        entry = self.gradebook.groups[0].entries[0]
        for color in entry.statuses.values():
            assert color.startswith("#")

    def test_first_entry_has_issue_urls(self) -> None:
        entry = self.gradebook.groups[0].entries[0]
        assert len(entry.issue_urls) > 0

    def test_issue_urls_are_paths(self) -> None:
        entry = self.gradebook.groups[0].entries[0]
        for url in entry.issue_urls.values():
            assert "/issue/" in url

    def test_first_entry_total_score(self) -> None:
        entry = self.gradebook.groups[0].entries[0]
        assert isinstance(entry.total_score, float)

    def test_max_scores_populated(self) -> None:
        group = self.gradebook.groups[0]
        assert len(group.max_scores) > 0

    def test_max_scores_are_numeric(self) -> None:
        group = self.gradebook.groups[0]
        for val in group.max_scores.values():
            assert isinstance(val, float)

    def test_all_groups_have_entries(self) -> None:
        for group in self.gradebook.groups:
            assert len(group.entries) > 0, f"Group {group.group_name} has no entries"

    def test_all_groups_have_tasks(self) -> None:
        for group in self.gradebook.groups:
            assert len(group.task_titles) > 0, f"Group {group.group_name} has no tasks"

    def test_different_groups_have_teachers(self) -> None:
        teachers = [g.teacher_name for g in self.gradebook.groups if g.teacher_name]
        assert len(teachers) >= 2


class TestGradebookNoGroups9002:
    def setup_method(self) -> None:
        html = build_gradebook_page(
            course_id=9002,
            groups=[
                GradebookGroupData(
                    group_id=2340,
                    group_name="ИИ > Прикладной Python 25'",
                    teacher_name="",
                    task_titles=["Streamlit", "Телеграм-бот"],
                    max_scores={"Streamlit": 12.0, "Телеграм-бот": 14.0},
                    entries=[
                        GradebookStudentRow(
                            student_name="Зефирчик Пётр",
                            student_url="/users/zefirchik/",
                            scores={"Streamlit": 10.0, "Телеграм-бот": 12.0},
                            statuses={"Streamlit": "#65E31B", "Телеграм-бот": "#65E31B"},
                            issue_urls={
                                "Streamlit": "/issue/get_or_create/80010/300100",
                            },
                            total_score=22.0,
                        ),
                    ],
                ),
            ],
        )
        self.gradebook = parse_gradebook_page(html, 9002)

    def test_course_id(self) -> None:
        assert self.gradebook.course_id == 9002

    def test_single_group(self) -> None:
        assert len(self.gradebook.groups) == 1

    def test_group_has_name(self) -> None:
        assert self.gradebook.groups[0].group_name

    def test_group_has_tasks(self) -> None:
        assert len(self.gradebook.groups[0].task_titles) > 0

    def test_group_has_entries(self) -> None:
        assert len(self.gradebook.groups[0].entries) > 0

    def test_entry_has_student_name(self) -> None:
        entry = self.gradebook.groups[0].entries[0]
        assert entry.student_name

    def test_entry_has_student_url(self) -> None:
        entry = self.gradebook.groups[0].entries[0]
        assert entry.student_url.startswith("/users/")

    def test_entry_has_scores(self) -> None:
        entry = self.gradebook.groups[0].entries[0]
        assert len(entry.scores) > 0

    def test_entry_has_total_score(self) -> None:
        entry = self.gradebook.groups[0].entries[0]
        assert isinstance(entry.total_score, float)

    def test_max_scores_populated(self) -> None:
        group = self.gradebook.groups[0]
        assert len(group.max_scores) > 0

    def test_no_teacher_name(self) -> None:
        group = self.gradebook.groups[0]
        assert group.teacher_name == ""

    def test_scores_match_task_titles(self) -> None:
        group = self.gradebook.groups[0]
        entry = group.entries[0]
        for task in entry.scores:
            assert task in group.task_titles


class TestGradebookEdgeCases:
    def test_empty_html(self) -> None:
        gradebook = parse_gradebook_page("<html><body></body></html>", 999)
        assert gradebook.course_id == 999
        assert len(gradebook.groups) == 0

    def test_no_tables(self) -> None:
        gradebook = parse_gradebook_page("<html><body><div>hello</div></body></html>", 123)
        assert len(gradebook.groups) == 0
