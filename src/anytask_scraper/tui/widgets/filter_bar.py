from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Container

from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Input, Select


def _is_blank_select_value(value: object) -> bool:
    return value is None or value is Select.NULL or value is Select.BLANK


def _serialize_select_value(select: Select[Any]) -> object | None:
    return None if _is_blank_select_value(select.value) else select.value


def _restore_select_value(select: Select[Any], value: object) -> None:
    if _is_blank_select_value(value):
        select.clear()
        return
    select.value = value


def _restore_select_value_from_options(
    select: Select[Any], value: object, valid_values: Container[object]
) -> None:
    if _is_blank_select_value(value) or value not in valid_values:
        select.clear()
        return
    select.value = value


class TaskFilterBar(Widget):
    @dataclass
    class Changed(Message):
        text: str
        status: str
        section: str

    @dataclass
    class Reset(Message):
        pass

    def __init__(
        self,
        statuses: list[str] | None = None,
        sections: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._statuses = statuses or []
        self._sections = sections or []

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search tasks...", id="task-filter-text")
        yield Select[str](
            [(s, s) for s in self._statuses],
            allow_blank=True,
            prompt="Status",
            id="task-filter-status",
        )
        yield Select[str](
            [(s, s) for s in self._sections],
            allow_blank=True,
            prompt="Section",
            id="task-filter-section",
        )

    def on_input_changed(self, event: Input.Changed) -> None:
        event.stop()
        self._emit_changed()

    def on_select_changed(self, event: Select.Changed) -> None:
        event.stop()
        self._emit_changed()

    def _emit_changed(self) -> None:
        text = self.query_one("#task-filter-text", Input).value.strip()
        status_val = self.query_one("#task-filter-status", Select).value
        section_val = self.query_one("#task-filter-section", Select).value

        status = "" if _is_blank_select_value(status_val) else str(status_val)
        section = "" if _is_blank_select_value(section_val) else str(section_val)

        self.post_message(self.Changed(text=text, status=status, section=section))

    def reset(self) -> None:
        self.query_one("#task-filter-text", Input).value = ""
        self.query_one("#task-filter-status", Select).clear()
        self.query_one("#task-filter-section", Select).clear()
        self._emit_changed()
        self.post_message(self.Reset())

    def save_state(self) -> dict[str, Any]:
        return {
            "text": self.query_one("#task-filter-text", Input).value,
            "status": _serialize_select_value(self.query_one("#task-filter-status", Select)),
            "section": _serialize_select_value(self.query_one("#task-filter-section", Select)),
        }

    def restore_state(self, state: dict[str, Any]) -> None:
        self.query_one("#task-filter-text", Input).value = state.get("text", "")
        _restore_select_value(self.query_one("#task-filter-status", Select), state.get("status"))
        _restore_select_value(self.query_one("#task-filter-section", Select), state.get("section"))
        self._emit_changed()

    def focus_text(self) -> None:
        self.query_one("#task-filter-text", Input).focus()

    def focus_next_filter(self) -> bool:
        focusable = [
            self.query_one("#task-filter-text", Input),
            self.query_one("#task-filter-status", Select),
            self.query_one("#task-filter-section", Select),
        ]
        for i, widget in enumerate(focusable):
            if widget.has_focus:
                if i == len(focusable) - 1:
                    return False
                focusable[i + 1].focus()
                return True
        focusable[0].focus()
        return True

    def focus_prev_filter(self) -> bool:
        focusable = [
            self.query_one("#task-filter-text", Input),
            self.query_one("#task-filter-status", Select),
            self.query_one("#task-filter-section", Select),
        ]
        for i, widget in enumerate(focusable):
            if widget.has_focus:
                if i == 0:
                    return False
                focusable[i - 1].focus()
                return True
        focusable[-1].focus()
        return True

    def update_options(
        self,
        statuses: list[str],
        sections: list[str],
    ) -> None:
        text_input = self.query_one("#task-filter-text", Input)
        status_select = self.query_one("#task-filter-status", Select)
        section_select = self.query_one("#task-filter-section", Select)
        current_text = text_input.value
        current_status = status_select.value
        current_section = section_select.value

        self._statuses = statuses
        self._sections = sections

        status_select.set_options([(s, s) for s in statuses])
        section_select.set_options([(s, s) for s in sections])
        _restore_select_value_from_options(status_select, current_status, set(statuses))
        _restore_select_value_from_options(section_select, current_section, set(sections))
        text_input.value = current_text


class QueueFilterBar(Widget):
    @dataclass
    class Changed(Message):
        text: str
        student: str
        task: str
        status: str
        reviewer: str

    @dataclass
    class Reset(Message):
        pass

    def __init__(
        self,
        students: list[str] | None = None,
        tasks: list[str] | None = None,
        statuses: list[str] | None = None,
        reviewers: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._students = students or []
        self._tasks = tasks or []
        self._statuses = statuses or []
        self._reviewers = reviewers or []

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search queue...", id="queue-filter-text")
        yield Select[str](
            [(s, s) for s in self._students],
            allow_blank=True,
            prompt="Student",
            id="queue-filter-student",
        )
        yield Select[str](
            [(t, t) for t in self._tasks],
            allow_blank=True,
            prompt="Task",
            id="queue-filter-task",
        )
        yield Select[str](
            [(s, s) for s in self._statuses],
            allow_blank=True,
            prompt="Status",
            id="queue-filter-status",
        )
        yield Select[str](
            [(r, r) for r in self._reviewers],
            allow_blank=True,
            prompt="Reviewer",
            id="queue-filter-reviewer",
        )

    def on_input_changed(self, event: Input.Changed) -> None:
        event.stop()
        self._emit_changed()

    def on_select_changed(self, event: Select.Changed) -> None:
        event.stop()
        self._emit_changed()

    def _emit_changed(self) -> None:
        text = self.query_one("#queue-filter-text", Input).value.strip()
        student_val = self.query_one("#queue-filter-student", Select).value
        task_val = self.query_one("#queue-filter-task", Select).value
        status_val = self.query_one("#queue-filter-status", Select).value
        reviewer_val = self.query_one("#queue-filter-reviewer", Select).value

        student = "" if _is_blank_select_value(student_val) else str(student_val)
        task = "" if _is_blank_select_value(task_val) else str(task_val)
        status = "" if _is_blank_select_value(status_val) else str(status_val)
        reviewer = "" if _is_blank_select_value(reviewer_val) else str(reviewer_val)

        self.post_message(
            self.Changed(text=text, student=student, task=task, status=status, reviewer=reviewer)
        )

    def reset(self) -> None:
        self.query_one("#queue-filter-text", Input).value = ""
        self.query_one("#queue-filter-student", Select).clear()
        self.query_one("#queue-filter-task", Select).clear()
        self.query_one("#queue-filter-status", Select).clear()
        self.query_one("#queue-filter-reviewer", Select).clear()
        self._emit_changed()
        self.post_message(self.Reset())

    def save_state(self) -> dict[str, Any]:
        return {
            "text": self.query_one("#queue-filter-text", Input).value,
            "student": _serialize_select_value(self.query_one("#queue-filter-student", Select)),
            "task": _serialize_select_value(self.query_one("#queue-filter-task", Select)),
            "status": _serialize_select_value(self.query_one("#queue-filter-status", Select)),
            "reviewer": _serialize_select_value(self.query_one("#queue-filter-reviewer", Select)),
        }

    def restore_state(self, state: dict[str, Any]) -> None:
        self.query_one("#queue-filter-text", Input).value = state.get("text", "")
        _restore_select_value(self.query_one("#queue-filter-student", Select), state.get("student"))
        _restore_select_value(self.query_one("#queue-filter-task", Select), state.get("task"))
        _restore_select_value(self.query_one("#queue-filter-status", Select), state.get("status"))
        _restore_select_value(
            self.query_one("#queue-filter-reviewer", Select), state.get("reviewer")
        )
        self._emit_changed()

    def focus_text(self) -> None:
        self.query_one("#queue-filter-text", Input).focus()

    def focus_next_filter(self) -> bool:
        focusable = [
            self.query_one("#queue-filter-text", Input),
            self.query_one("#queue-filter-student", Select),
            self.query_one("#queue-filter-task", Select),
            self.query_one("#queue-filter-status", Select),
            self.query_one("#queue-filter-reviewer", Select),
        ]
        for i, widget in enumerate(focusable):
            if widget.has_focus:
                if i == len(focusable) - 1:
                    return False
                focusable[i + 1].focus()
                return True
        focusable[0].focus()
        return True

    def focus_prev_filter(self) -> bool:
        focusable = [
            self.query_one("#queue-filter-text", Input),
            self.query_one("#queue-filter-student", Select),
            self.query_one("#queue-filter-task", Select),
            self.query_one("#queue-filter-status", Select),
            self.query_one("#queue-filter-reviewer", Select),
        ]
        for i, widget in enumerate(focusable):
            if widget.has_focus:
                if i == 0:
                    return False
                focusable[i - 1].focus()
                return True
        focusable[-1].focus()
        return True

    def update_options(
        self,
        students: list[str],
        tasks: list[str],
        statuses: list[str],
        reviewers: list[str] | None = None,
    ) -> None:
        text_input = self.query_one("#queue-filter-text", Input)
        student_select = self.query_one("#queue-filter-student", Select)
        task_select = self.query_one("#queue-filter-task", Select)
        status_select = self.query_one("#queue-filter-status", Select)
        reviewer_select = self.query_one("#queue-filter-reviewer", Select)
        current_text = text_input.value
        current_student = student_select.value
        current_task = task_select.value
        current_status = status_select.value
        current_reviewer = reviewer_select.value

        self._students = students
        self._tasks = tasks
        self._statuses = statuses
        if reviewers is not None:
            self._reviewers = reviewers

        student_select.set_options([(s, s) for s in students])
        task_select.set_options([(t, t) for t in tasks])
        status_select.set_options([(s, s) for s in statuses])
        if reviewers is not None:
            reviewer_select.set_options([(r, r) for r in reviewers])
        _restore_select_value_from_options(student_select, current_student, set(students))
        _restore_select_value_from_options(task_select, current_task, set(tasks))
        _restore_select_value_from_options(status_select, current_status, set(statuses))
        current_reviewers = set(reviewers or self._reviewers)
        _restore_select_value_from_options(reviewer_select, current_reviewer, current_reviewers)
        text_input.value = current_text


class GradebookFilterBar(Widget):
    @dataclass
    class Changed(Message):
        text: str
        group: str
        teacher: str

    @dataclass
    class Reset(Message):
        pass

    def __init__(
        self,
        groups: list[str] | None = None,
        teachers: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._groups = groups or []
        self._teachers = teachers or []

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search students...", id="gb-filter-text")
        yield Select[str](
            [(g, g) for g in self._groups],
            allow_blank=True,
            prompt="Group",
            id="gb-filter-group",
        )
        yield Select[str](
            [(t, t) for t in self._teachers],
            allow_blank=True,
            prompt="Teacher",
            id="gb-filter-teacher",
        )

    def on_input_changed(self, event: Input.Changed) -> None:
        event.stop()
        self._emit_changed()

    def on_select_changed(self, event: Select.Changed) -> None:
        event.stop()
        self._emit_changed()

    def _emit_changed(self) -> None:
        text = self.query_one("#gb-filter-text", Input).value.strip()
        group_val = self.query_one("#gb-filter-group", Select).value
        teacher_val = self.query_one("#gb-filter-teacher", Select).value

        group = "" if _is_blank_select_value(group_val) else str(group_val)
        teacher = "" if _is_blank_select_value(teacher_val) else str(teacher_val)

        self.post_message(self.Changed(text=text, group=group, teacher=teacher))

    def reset(self) -> None:
        self.query_one("#gb-filter-text", Input).value = ""
        self.query_one("#gb-filter-group", Select).clear()
        self.query_one("#gb-filter-teacher", Select).clear()
        self._emit_changed()
        self.post_message(self.Reset())

    def save_state(self) -> dict[str, Any]:
        return {
            "text": self.query_one("#gb-filter-text", Input).value,
            "group": _serialize_select_value(self.query_one("#gb-filter-group", Select)),
            "teacher": _serialize_select_value(self.query_one("#gb-filter-teacher", Select)),
        }

    def restore_state(self, state: dict[str, Any]) -> None:
        self.query_one("#gb-filter-text", Input).value = state.get("text", "")
        _restore_select_value(self.query_one("#gb-filter-group", Select), state.get("group"))
        _restore_select_value(self.query_one("#gb-filter-teacher", Select), state.get("teacher"))
        self._emit_changed()

    def focus_text(self) -> None:
        self.query_one("#gb-filter-text", Input).focus()

    def focus_next_filter(self) -> bool:
        focusable = [
            self.query_one("#gb-filter-text", Input),
            self.query_one("#gb-filter-group", Select),
            self.query_one("#gb-filter-teacher", Select),
        ]
        for i, widget in enumerate(focusable):
            if widget.has_focus:
                if i == len(focusable) - 1:
                    return False
                focusable[i + 1].focus()
                return True
        focusable[0].focus()
        return True

    def focus_prev_filter(self) -> bool:
        focusable = [
            self.query_one("#gb-filter-text", Input),
            self.query_one("#gb-filter-group", Select),
            self.query_one("#gb-filter-teacher", Select),
        ]
        for i, widget in enumerate(focusable):
            if widget.has_focus:
                if i == 0:
                    return False
                focusable[i - 1].focus()
                return True
        focusable[-1].focus()
        return True

    def update_options(
        self,
        groups: list[str],
        teachers: list[str],
    ) -> None:
        text_input = self.query_one("#gb-filter-text", Input)
        group_select = self.query_one("#gb-filter-group", Select)
        teacher_select = self.query_one("#gb-filter-teacher", Select)
        current_text = text_input.value
        current_group = group_select.value
        current_teacher = teacher_select.value

        self._groups = groups
        self._teachers = teachers

        group_select.set_options([(g, g) for g in groups])
        teacher_select.set_options([(t, t) for t in teachers])
        _restore_select_value_from_options(group_select, current_group, set(groups))
        _restore_select_value_from_options(teacher_select, current_teacher, set(teachers))
        text_input.value = current_text
