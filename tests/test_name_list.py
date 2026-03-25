from __future__ import annotations

from anytask_scraper._queue_helpers import filter_queue_entries
from anytask_scraper.models import (
    Gradebook,
    GradebookEntry,
    GradebookGroup,
    QueueEntry,
    check_name_list_matches,
    filter_gradebook,
    name_matches_list,
    parse_name_list,
)


def _make_queue_entry(student_name: str, task_title: str = "Task") -> QueueEntry:
    return QueueEntry(
        student_name=student_name,
        student_url=f"/users/{student_name.lower().replace(' ', '_')}/",
        task_title=task_title,
        update_time="2025-01-01 00:00",
        mark="",
        status_color="#ccc",
        status_name="Новый",
        responsible_name="",
        responsible_url="",
        has_issue_access=False,
        issue_url="",
    )


def _make_gradebook_entry(student_name: str, total_score: float = 0.0) -> GradebookEntry:
    return GradebookEntry(
        student_name=student_name,
        student_url=f"/users/{student_name.lower().replace(' ', '_')}/",
        total_score=total_score,
    )


def _make_gradebook(entries: list[GradebookEntry]) -> Gradebook:
    group = GradebookGroup(
        group_name="Test Group",
        group_id=1,
        teacher_name="Teacher",
        task_titles=["Task1"],
        max_scores={"Task1": 10.0},
        entries=entries,
    )
    return Gradebook(course_id=42, groups=[group])


class TestParseNameList:
    def test_empty_string(self) -> None:
        assert parse_name_list("") == []

    def test_whitespace_only(self) -> None:
        assert parse_name_list("   \n  \n\t  ") == []

    def test_single_name(self) -> None:
        assert parse_name_list("Иванов Иван") == ["Иванов Иван"]

    def test_multiple_names(self) -> None:
        result = parse_name_list("Иванов Иван\nПетров Пётр\nСидоров Сид")
        assert result == ["Иванов Иван", "Петров Пётр", "Сидоров Сид"]

    def test_duplicates_removed_preserving_order(self) -> None:
        result = parse_name_list("Иванов\nПетров\nИванов\nСидоров\nПетров")
        assert result == ["Иванов", "Петров", "Сидоров"]

    def test_blank_lines_stripped(self) -> None:
        result = parse_name_list("\nИванов\n\nПетров\n")
        assert result == ["Иванов", "Петров"]

    def test_leading_trailing_spaces_stripped_per_line(self) -> None:
        result = parse_name_list("  Иванов Иван  \n  Петров Пётр  ")
        assert result == ["Иванов Иван", "Петров Пётр"]

    def test_windows_line_endings(self) -> None:
        result = parse_name_list("Иванов\r\nПетров")
        assert result == ["Иванов", "Петров"]

    def test_order_preserved_not_sorted(self) -> None:
        result = parse_name_list("Яблоков\nАбрамов\nМихайлов")
        assert result == ["Яблоков", "Абрамов", "Михайлов"]

    def test_single_blank_line(self) -> None:
        assert parse_name_list("\n") == []


class TestNameMatchesList:
    def test_empty_list_returns_true(self) -> None:
        assert name_matches_list("Иванов Иван Иванович", []) is True

    def test_exact_match(self) -> None:
        assert name_matches_list("Иванов", ["Иванов"]) is True

    def test_prefix_match_last_name_only(self) -> None:
        assert name_matches_list("Иванов Иван Иванович", ["Иванов"]) is True

    def test_full_name_entry_matches_full_name(self) -> None:
        assert name_matches_list("Петров Пётр", ["Петров Пётр"]) is True

    def test_case_insensitive_match(self) -> None:
        assert name_matches_list("ИВАНОВ Иван", ["иванов"]) is True

    def test_case_insensitive_mixed(self) -> None:
        assert name_matches_list("иванов иван", ["Иванов"]) is True

    def test_no_match(self) -> None:
        assert name_matches_list("Петров Пётр", ["Иванов", "Сидоров"]) is False

    def test_matches_first_in_list(self) -> None:
        assert name_matches_list("Иванов Иван", ["Иванов", "Петров"]) is True

    def test_matches_second_in_list(self) -> None:
        assert name_matches_list("Петров Пётр", ["Иванов", "Петров"]) is True

    def test_partial_word_not_a_prefix(self) -> None:
        assert name_matches_list("Иванов Иван", ["ванов"]) is False

    def test_entry_longer_than_name_no_match(self) -> None:
        assert name_matches_list("Иван", ["Иванов"]) is False

    def test_similar_surname_not_matched(self) -> None:
        assert name_matches_list("Иванова Мария", ["Иванов"]) is False

    def test_prefix_match_requires_word_boundary(self) -> None:
        assert name_matches_list("Иванов Иван", ["Иванов"]) is True
        assert name_matches_list("Ивановский Пётр", ["Иванов"]) is False


class TestCheckNameListMatches:
    def test_empty_name_list_returns_empty_tuples(self) -> None:
        matched, unmatched = check_name_list_matches(["Иванов Иван", "Петров Пётр"], [])
        assert matched == []
        assert unmatched == []

    def test_all_matched(self) -> None:
        student_names = ["Иванов Иван Иванович", "Петров Пётр Петрович"]
        name_list = ["Иванов", "Петров"]
        matched, unmatched = check_name_list_matches(student_names, name_list)
        assert matched == ["Иванов", "Петров"]
        assert unmatched == []

    def test_partial_match(self) -> None:
        student_names = ["Иванов Иван", "Петров Пётр"]
        name_list = ["Иванов", "Сидоров"]
        matched, unmatched = check_name_list_matches(student_names, name_list)
        assert matched == ["Иванов"]
        assert unmatched == ["Сидоров"]

    def test_none_matched(self) -> None:
        student_names = ["Иванов Иван", "Петров Пётр"]
        name_list = ["Сидоров", "Козлов"]
        matched, unmatched = check_name_list_matches(student_names, name_list)
        assert matched == []
        assert unmatched == ["Сидоров", "Козлов"]

    def test_empty_student_list(self) -> None:
        matched, unmatched = check_name_list_matches([], ["Иванов"])
        assert matched == []
        assert unmatched == ["Иванов"]

    def test_case_insensitive(self) -> None:
        student_names = ["ИВАНОВ ИВАН"]
        matched, unmatched = check_name_list_matches(student_names, ["иванов"])
        assert matched == ["иванов"]
        assert unmatched == []

    def test_order_preserved(self) -> None:
        student_names = ["Яблоков Яков", "Абрамов Артём", "Михайлов Михаил"]
        name_list = ["Михайлов", "Абрамов", "Яблоков"]
        matched, unmatched = check_name_list_matches(student_names, name_list)
        assert matched == ["Михайлов", "Абрамов", "Яблоков"]
        assert unmatched == []

    def test_duplicate_entry_matched_once(self) -> None:
        student_names = ["Иванов Иван"]
        matched, unmatched = check_name_list_matches(student_names, ["Иванов", "Иванов"])
        assert matched == ["Иванов", "Иванов"]
        assert unmatched == []


class TestFilterQueueEntriesNameList:
    def setup_method(self) -> None:
        self.entries = [
            _make_queue_entry("Иванов Иван Иванович"),
            _make_queue_entry("Петров Пётр Петрович"),
            _make_queue_entry("Сидоров Сидор Сидорович"),
        ]

    def test_none_name_list_returns_all(self) -> None:
        result = filter_queue_entries(self.entries, name_list=None)
        assert len(result) == 3

    def test_empty_name_list_returns_all(self) -> None:
        result = filter_queue_entries(self.entries, name_list=[])
        assert len(result) == 3

    def test_single_prefix_filters_correctly(self) -> None:
        result = filter_queue_entries(self.entries, name_list=["Иванов"])
        assert len(result) == 1
        assert result[0].student_name == "Иванов Иван Иванович"

    def test_multiple_prefixes_filter_correctly(self) -> None:
        result = filter_queue_entries(self.entries, name_list=["Иванов", "Петров"])
        names = [e.student_name for e in result]
        assert "Иванов Иван Иванович" in names
        assert "Петров Пётр Петрович" in names
        assert "Сидоров Сидор Сидорович" not in names

    def test_no_match_returns_empty(self) -> None:
        result = filter_queue_entries(self.entries, name_list=["Козлов"])
        assert result == []

    def test_case_insensitive_filter(self) -> None:
        result = filter_queue_entries(self.entries, name_list=["иванов"])
        assert len(result) == 1
        assert result[0].student_name == "Иванов Иван Иванович"

    def test_name_list_combined_with_task_filter(self) -> None:
        entries = [
            _make_queue_entry("Иванов Иван", task_title="Numpy"),
            _make_queue_entry("Иванов Иван", task_title="Pandas"),
            _make_queue_entry("Петров Пётр", task_title="Numpy"),
        ]
        result = filter_queue_entries(entries, filter_task="numpy", name_list=["Иванов"])
        assert len(result) == 1
        assert result[0].task_title == "Numpy"
        assert result[0].student_name == "Иванов Иван"


class TestFilterGradebookNameList:
    def setup_method(self) -> None:
        entries = [
            _make_gradebook_entry("Иванов Иван Иванович", total_score=8.0),
            _make_gradebook_entry("Петров Пётр Петрович", total_score=5.0),
            _make_gradebook_entry("Сидоров Сидор Сидорович", total_score=9.0),
        ]
        self.gradebook = _make_gradebook(entries)

    def test_none_name_list_no_filtering(self) -> None:
        result = filter_gradebook(self.gradebook, name_list=None)
        assert len(result.groups[0].entries) == 3

    def test_empty_name_list_no_filtering(self) -> None:
        result = filter_gradebook(self.gradebook, name_list=[])
        assert len(result.groups[0].entries) == 3

    def test_single_prefix_filters_entries(self) -> None:
        result = filter_gradebook(self.gradebook, name_list=["Иванов"])
        entries = result.groups[0].entries
        assert len(entries) == 1
        assert entries[0].student_name == "Иванов Иван Иванович"

    def test_multiple_prefixes_filter_entries(self) -> None:
        result = filter_gradebook(self.gradebook, name_list=["Иванов", "Петров"])
        entries = result.groups[0].entries
        names = [e.student_name for e in entries]
        assert "Иванов Иван Иванович" in names
        assert "Петров Пётр Петрович" in names
        assert "Сидоров Сидор Сидорович" not in names

    def test_no_match_yields_no_entries(self) -> None:
        result = filter_gradebook(self.gradebook, name_list=["Козлов"])
        assert all(len(g.entries) == 0 for g in result.groups)

    def test_case_insensitive_filter(self) -> None:
        result = filter_gradebook(self.gradebook, name_list=["петров"])
        entries = result.groups[0].entries
        assert len(entries) == 1
        assert entries[0].student_name == "Петров Пётр Петрович"

    def test_original_gradebook_not_mutated(self) -> None:
        original_count = len(self.gradebook.groups[0].entries)
        filter_gradebook(self.gradebook, name_list=["Иванов"])
        assert len(self.gradebook.groups[0].entries) == original_count

    def test_course_id_preserved(self) -> None:
        result = filter_gradebook(self.gradebook, name_list=["Иванов"])
        assert result.course_id == 42

    def test_group_metadata_preserved(self) -> None:
        result = filter_gradebook(self.gradebook, name_list=["Иванов"])
        group = result.groups[0]
        assert group.group_name == "Test Group"
        assert group.group_id == 1
        assert group.teacher_name == "Teacher"

    def test_name_list_combined_with_min_score(self) -> None:
        result = filter_gradebook(self.gradebook, name_list=["Иванов", "Петров"], min_score=6.0)
        entries = result.groups[0].entries
        names = [e.student_name for e in entries]
        assert "Иванов Иван Иванович" in names
        assert "Петров Пётр Петрович" not in names

    def test_multiple_groups_filtered_independently(self) -> None:
        group_a = GradebookGroup(
            group_name="Group A",
            group_id=1,
            teacher_name="Teacher A",
            task_titles=["Task1"],
            max_scores={"Task1": 10.0},
            entries=[
                _make_gradebook_entry("Иванов Иван"),
                _make_gradebook_entry("Козлов Козёл"),
            ],
        )
        group_b = GradebookGroup(
            group_name="Group B",
            group_id=2,
            teacher_name="Teacher B",
            task_titles=["Task1"],
            max_scores={"Task1": 10.0},
            entries=[
                _make_gradebook_entry("Петров Пётр"),
                _make_gradebook_entry("Иванов Алексей"),
            ],
        )
        gradebook = Gradebook(course_id=99, groups=[group_a, group_b])
        result = filter_gradebook(gradebook, name_list=["Иванов"])

        assert len(result.groups) == 2
        assert all(e.student_name.startswith("Иванов") for g in result.groups for e in g.entries)
