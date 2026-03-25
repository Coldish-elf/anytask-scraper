from __future__ import annotations

from anytask_scraper.models import QueueEntry, last_name_in_range, name_matches_list


def parse_ajax_entry(row: dict[str, object]) -> QueueEntry:
    return QueueEntry(
        student_name=str(row.get("student_name", "")),
        student_url=str(row.get("student_url", "")),
        task_title=str(row.get("task_title", "")),
        update_time=str(row.get("update_time", "")),
        mark=str(row.get("mark", "")),
        status_color=str(row.get("status_color", "")),
        status_name=str(row.get("status_name", "")),
        responsible_name=str(row.get("responsible_name", "")),
        responsible_url=str(row.get("responsible_url", "")),
        has_issue_access=bool(row.get("has_issue_access", False)),
        issue_url=str(row.get("issue_url", "")),
    )


def filter_queue_entries(
    entries: list[QueueEntry],
    *,
    filter_task: str = "",
    filter_reviewer: str = "",
    filter_status: str = "",
    last_name_from: str = "",
    last_name_to: str = "",
    name_list: list[str] | None = None,
) -> list[QueueEntry]:
    filtered = entries
    if filter_task:
        needle = filter_task.lower()
        filtered = [e for e in filtered if needle in e.task_title.lower()]
    if filter_reviewer:
        needle = filter_reviewer.lower()
        filtered = [e for e in filtered if needle in e.responsible_name.lower()]
    if filter_status:
        needle = filter_status.lower()
        filtered = [e for e in filtered if needle in e.status_name.lower()]
    if last_name_from or last_name_to:
        filtered = [
            e for e in filtered if last_name_in_range(e.student_name, last_name_from, last_name_to)
        ]
    if name_list:
        filtered = [e for e in filtered if name_matches_list(e.student_name, name_list)]
    return filtered
