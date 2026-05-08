from __future__ import annotations

import asyncio

from textual.app import App, ComposeResult
from textual.widgets import Select

from anytask_scraper.tui.widgets.filter_bar import GradebookFilterBar, QueueFilterBar, TaskFilterBar


def test_task_filter_bar_mounts_with_blank_selects() -> None:
    class TestApp(App[None]):
        def compose(self) -> ComposeResult:
            yield TaskFilterBar(statuses=["Open"], sections=["Week 1"])

    async def run() -> None:
        app = TestApp()
        async with app.run_test():
            bar = app.query_one(TaskFilterBar)
            assert bar.query_one("#task-filter-status", Select).is_blank()
            assert bar.query_one("#task-filter-section", Select).is_blank()

    asyncio.run(run())


def test_restore_state_treats_legacy_false_values_as_blank() -> None:
    class TestApp(App[None]):
        def compose(self) -> ComposeResult:
            yield TaskFilterBar(statuses=["Open"], sections=["Week 1"], id="task-bar")
            yield QueueFilterBar(
                students=["Alice"],
                tasks=["HW 1"],
                statuses=["Open"],
                reviewers=["Bob"],
                id="queue-bar",
            )
            yield GradebookFilterBar(groups=["A-01"], teachers=["Bob"], id="gradebook-bar")

    async def run() -> None:
        app = TestApp()
        async with app.run_test():
            task_bar = app.query_one("#task-bar", TaskFilterBar)
            task_bar.restore_state({"status": False, "section": False})
            assert task_bar.query_one("#task-filter-status", Select).is_blank()
            assert task_bar.query_one("#task-filter-section", Select).is_blank()

            queue_bar = app.query_one("#queue-bar", QueueFilterBar)
            queue_bar.restore_state(
                {"student": False, "task": False, "status": False, "reviewer": False}
            )
            assert queue_bar.query_one("#queue-filter-student", Select).is_blank()
            assert queue_bar.query_one("#queue-filter-task", Select).is_blank()
            assert queue_bar.query_one("#queue-filter-status", Select).is_blank()
            assert queue_bar.query_one("#queue-filter-reviewer", Select).is_blank()

            gradebook_bar = app.query_one("#gradebook-bar", GradebookFilterBar)
            gradebook_bar.restore_state({"group": False, "teacher": False})
            assert gradebook_bar.query_one("#gb-filter-group", Select).is_blank()
            assert gradebook_bar.query_one("#gb-filter-teacher", Select).is_blank()

    asyncio.run(run())
