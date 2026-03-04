"""Builders that generate minimal HTML snippets for parser tests."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class StudentTask:
    """Parameters for one task row in student view."""

    task_id: int
    title: str
    score: str = "0.0"
    status: str = ""
    status_color: str = "#ccc"
    deadline: str = ""
    submit_url: str = ""
    description_html: str = ""


def build_student_course_page(
    *,
    course_id: int = 9001,
    title: str = "Python",
    teachers: list[str] | None = None,
    tasks: list[StudentTask] | None = None,
) -> str:
    if teachers is None:
        teachers = ["Бублик Сергей"]
    if tasks is None:
        tasks = []

    teacher_links = ", ".join(
        f'<a href="/accounts/profile/t{i}">{t}</a>' for i, t in enumerate(teachers)
    )

    task_rows = []
    collapse_divs = []
    for t in tasks:
        submit_col = ""
        if t.submit_url:
            submit_col = (
                f'<div style="width: 15%">'
                f'<a class="btn btn-sm btn-primary" href="{t.submit_url}">Сдать</a>'
                f"</div>"
            )

        status_span = ""
        if t.status:
            status_span = (
                f'<span class="label" style="background-color:{t.status_color}"> {t.status}</span>'
            )

        task_rows.append(
            f'<div class="tasks-list">'
            f'<div style="width: 40%;">'
            f'<a data-toggle="collapse" href="#collapse_{t.task_id}"'
            f' aria-controls="collapse_{t.task_id}">{t.title}</a>'
            f"</div>"
            f'<div style="width: 10%">{t.score}</div>'
            f'<div style="width: 15%">{status_span}</div>'
            f'<div style="width: 20%">сдать до {t.deadline}</div>'
            f"{submit_col}"
            f"</div>"
        )

        if t.description_html:
            collapse_divs.append(
                f'<div class="collapse" id="collapse_{t.task_id}">'
                f'<div style="width: 100%">{t.description_html}</div>'
                f"</div>"
            )

    return (
        f"<html><body>"
        f'<h5 class="card-title">{title}</h5>'
        f'<p class="card-text course_teachers">Преподаватели: {teacher_links}</p>'
        f'<div id="tasks-tab">'
        f'<div id="tasks-table">' + "\n".join(task_rows) + "\n".join(collapse_divs) + "</div></div>"
        "</body></html>"
    )


@dataclass
class TeacherTask:
    """Parameters for one task row in teacher view."""

    task_id: int
    title: str
    edit_url: str = ""
    max_score: str = ""
    deadline: str = ""


@dataclass
class TeacherGroup:
    """A group (section) in teacher view."""

    group_id: int
    section_name: str
    tasks: list[TeacherTask] = field(default_factory=list)


def build_teacher_course_page(
    *,
    course_id: int = 9002,
    title: str = "Python",
    teachers: list[str] | None = None,
    groups: list[TeacherGroup] | None = None,
) -> str:
    if teachers is None:
        teachers = ["Бублик Сергей"]
    if groups is None:
        groups = []

    teacher_links = ", ".join(
        f'<a href="/accounts/profile/t{i}">{t}</a>' for i, t in enumerate(teachers)
    )

    group_html_parts = []
    for g in groups:
        task_rows = []
        for t in g.tasks:
            edit_col = ""
            if t.edit_url:
                edit_col = (
                    f'<a class="btn btn-secondary btn-sm"'
                    f' href="{t.edit_url}">'
                    f'<span class="fa fa-pencil"></span></a>'
                )

            score_span = ""
            if t.max_score:
                score_span = f'<span class="label label-inverse">{t.max_score}</span>'

            task_rows.append(
                f'<div class="tasks-list">'
                f'<div style="width: 35%;">{t.title}</div>'
                f'<div style="width: 10%;">{edit_col}</div>'
                f'<div style="width: 10%">{score_span}</div>'
                f'<div style="width: 25%">сдать до {t.deadline}</div>'
                f'<div style="width: 20%"></div>'
                f"</div>"
            )

        header = (
            f"<div>"
            f"<h6>"
            f'<a class="btn btn-secondary btn-sm" data-toggle="collapse"'
            f' href="#collapse_group_{g.group_id}"></a>'
            f"{g.section_name}"
            f"</h6>"
            f"</div>"
        )

        group_html_parts.append(
            f'{header}<div id="collapse_group_{g.group_id}">' + "\n".join(task_rows) + "</div>"
        )

    return (
        f"<html><body>"
        f'<h5 class="card-title">{title}</h5>'
        f'<p class="card-text course_teachers">Преподаватели: {teacher_links}</p>'
        f'<div id="tasks-tab">'
        f'<div id="tasks-table">' + "\n".join(group_html_parts) + "</div></div>"
        "</body></html>"
    )


def build_profile_page(
    *,
    teacher_courses: list[tuple[int, str]] | None = None,
    student_courses: list[tuple[int, str]] | None = None,
) -> str:
    teacher_courses = teacher_courses or []
    student_courses = student_courses or []

    teacher_items = "\n".join(
        f'<li class="list-group-item"><a href="/course/{cid}">{name}</a></li>'
        for cid, name in teacher_courses
    )
    student_items = "\n".join(
        f'<li class="list-group-item"><a href="/course/{cid}">{name}</a></li>'
        for cid, name in student_courses
    )

    parts = ["<html><body>"]
    if teacher_courses:
        parts.append(f'<div id="teacher_course">{teacher_items}</div>')
    if student_courses:
        parts.append(f'<div id="course_list">{student_items}</div>')
    parts.append("</body></html>")
    return "\n".join(parts)


def build_queue_page(
    *,
    students: list[tuple[str, str]] | None = None,
    tasks: list[tuple[str, str]] | None = None,
    reviewers: list[tuple[str, str]] | None = None,
    statuses: list[tuple[str, str]] | None = None,
    csrf_token: str = "test-csrf-token-abcdefghij1234567890",
) -> str:
    students = students or []
    tasks = tasks or []
    reviewers = reviewers or []
    statuses = statuses or []

    def _options(items: list[tuple[str, str]]) -> str:
        return "\n".join(f'<option value="{val}">{name}</option>' for val, name in items)

    return (
        f"<html><body>"
        f"<script>"
        f"$.post('/set_lang/', {{'lang': lang, 'csrfmiddlewaretoken': \"{csrf_token}\",}});"
        f"</script>"
        f'<div id="modal_filter">'
        f'<select name="students">{_options(students)}</select>'
        f'<select name="task">{_options(tasks)}</select>'
        f'<select name="responsible">{_options(reviewers)}</select>'
        f'<select name="status_field">{_options(statuses)}</select>'
        f"</div>"
        f"</body></html>"
    )


@dataclass
class SubmissionComment:
    """Parameters for one comment in submission page."""

    author_name: str = ""
    author_url: str = ""
    timestamp: str = ""
    content_html: str = ""
    files: list[SubmissionFile] = field(default_factory=list)
    is_after_deadline: bool = False
    is_system_event: bool = False


@dataclass
class SubmissionFile:
    """A file attachment in a comment."""

    filename: str = ""
    download_url: str = ""
    is_notebook: bool = False


@dataclass
class SubmissionForms:
    """Which forms to render on the submission page."""

    has_grade_form: bool = False
    has_status_form: bool = False
    has_comment_form: bool = False
    max_score: str = ""
    status_options: list[tuple[int, str, bool]] = field(default_factory=list)
    issue_id: int = 0


def build_submission_page(
    *,
    issue_id: int = 500001,
    task_title: str = "",
    student_name: str = "",
    student_url: str = "",
    reviewer_name: str = "",
    reviewer_url: str = "",
    status: str = "",
    grade: str = "",
    max_score: str = "",
    deadline: str = "",
    csrf_token: str = "test-csrf-token-abcdefghij1234567890",
    comments: list[SubmissionComment] | None = None,
    forms: SubmissionForms | None = None,
) -> str:
    comments = comments or []

    meta_cards = []

    def _card(label: str, result_html: str) -> str:
        return (
            f'<div class="card">'
            f'<div class="col-md-5 accordion2-label">{label}:</div>'
            f'<div class="col-md-7 accordion2-result">{result_html}</div>'
            f"</div>"
        )

    if task_title:
        meta_cards.append(
            _card("Задача", f'<a href="#" id="modal_task_description_btn">{task_title}</a>')
        )
    if student_name:
        meta_cards.append(
            _card("Студент", f'<a class="user" href="{student_url}">{student_name}</a>')
        )
    if reviewer_name:
        meta_cards.append(
            _card("Проверяющий", f'<a class="user" href="{reviewer_url}">{reviewer_name}</a>')
        )
    elif reviewer_name == "":
        meta_cards.append(_card("Проверяющий", "---"))
    if status:
        meta_cards.append(_card("Статус", status))
    if grade or max_score:
        grade_text = f"{grade} из {max_score}" if max_score else grade
        meta_cards.append(_card("Оценка", grade_text))
    if deadline:
        meta_cards.append(_card("Дата сдачи", f"{deadline} 00:00"))

    comment_items = []
    for c in comments:
        after_class = " after_deadline" if c.is_after_deadline else ""

        author_html = ""
        if c.author_name:
            author_html = (
                f'<strong><a class="card-link" href="{c.author_url}">{c.author_name}</a></strong>'
            )

        time_html = ""
        if c.timestamp:
            time_html = f'<small class="text-muted">{c.timestamp}</small>'

        content_html = ""
        if c.is_system_event:
            content_html = f"<p>{c.content_html}</p>"
        else:
            content_html = f'<div class="issue-page-comment">{c.content_html}</div>'

        files_html = ""
        if c.files:
            file_parts = []
            for f in c.files:
                if f.is_notebook:
                    file_parts.append(
                        f'<div class="ipynb-file-link">'
                        f'<a class="dropdown-toggle" href="#">{f.filename}</a>'
                        f'<div class="dropdown-menu">'
                        f'<a class="dropdown-item" href="{f.download_url}">Скачать</a>'
                        f"</div></div>"
                    )
                else:
                    file_parts.append(f'<a href="{f.download_url}">{f.filename}</a>')
            files_html = f'<div class="files">{"".join(file_parts)}</div>'

        comment_items.append(
            f"<li>"
            f'<div class="row">'
            f"{author_html}"
            f"{time_html}"
            f'<div class="history-body{after_class}">'
            f"{content_html}"
            f"</div>"
            f"{files_html}"
            f"</div>"
            f"</li>"
        )

    forms_html = ""
    if forms:
        csrf_input = f'<input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">'
        issue_input = f'<input type="hidden" name="issue_id" value="{forms.issue_id}">'

        if forms.has_grade_form:
            max_input = ""
            if forms.max_score:
                max_input = f'<input type="hidden" id="max_mark" value="{forms.max_score}">'
            forms_html += f'<form id="mark_form">{csrf_input}{issue_input}{max_input}</form>'
        if forms.has_status_form:
            options = ""
            for code, label, selected in forms.status_options:
                sel = ' selected="selected"' if selected else ""
                options += f'<option value="{code}"{sel}>{label}</option>'
            forms_html += (
                f'<form id="status_form">{csrf_input}{issue_input}'
                f'<select name="status">{options}</select></form>'
            )
        if forms.has_comment_form:
            forms_html += f'<form id="fileupload">{csrf_input}{issue_input}</form>'
    elif csrf_token:
        forms_html = (
            f'<input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">'
            f'<input type="hidden" name="issue_id" value="{issue_id}">'
        )

    breadcrumb = f"Issue: {issue_id}"

    return (
        f"<html><body>"
        f"{breadcrumb}"
        f'<div id="accordion2">{"".join(meta_cards)}</div>'
        f'<ul class="history">{"".join(comment_items)}</ul>'
        f"{forms_html}"
        f"</body></html>"
    )


@dataclass
class GradebookStudentRow:
    """One student row for gradebook builder."""

    student_name: str
    student_url: str
    scores: dict[str, float] = field(default_factory=dict)
    statuses: dict[str, str] = field(default_factory=dict)
    issue_urls: dict[str, str] = field(default_factory=dict)
    total_score: float = 0.0


@dataclass
class GradebookGroupData:
    """One gradebook group (table)."""

    group_id: int
    group_name: str
    teacher_name: str = ""
    task_titles: list[str] = field(default_factory=list)
    max_scores: dict[str, float] = field(default_factory=dict)
    entries: list[GradebookStudentRow] = field(default_factory=list)


def build_gradebook_page(
    *,
    course_id: int = 9003,
    groups: list[GradebookGroupData] | None = None,
) -> str:
    groups = groups or []

    tables = []
    for g in groups:
        card_links = f'<a class="card-link" href="#">{g.group_name}</a>'
        if g.teacher_name:
            card_links += f' <a class="card-link" href="#">{g.teacher_name}</a>'

        header_ths = "<th>#</th><th>Студент</th>"
        for title in g.task_titles:
            max_span = ""
            if title in g.max_scores:
                max_span = f'<span class="label-inverse">{g.max_scores[title]}</span>'
            header_ths += f'<th class="dom-number word-wrap"><a href="#">{title}</a>{max_span}</th>'
        header_ths += "<th>Сумма</th>"

        body_rows = []
        for idx, entry in enumerate(g.entries, 1):
            tds = f"<td>{idx}</td>"
            tds += (
                f'<td><a class="card-link" href="{entry.student_url}">{entry.student_name}</a></td>'
            )
            for title in g.task_titles:
                score_val = entry.scores.get(title, 0.0)
                color = entry.statuses.get(title, "#ccc")
                issue = entry.issue_urls.get(title, "")
                link_open = f'<a href="{issue}">' if issue else ""
                link_close = "</a>" if issue else ""
                tds += (
                    f"<td>{link_open}"
                    f'<span class="label" style="background-color: {color}">'
                    f"{score_val}</span>"
                    f"{link_close}</td>"
                )
            tds += f'<td class="sum-score"><span class="label">{entry.total_score}</span></td>'
            body_rows.append(f"<tr>{tds}</tr>")

        tables.append(
            f'<div class="card">'
            f'<h5 class="card-title">{card_links}</h5>'
            f'<table class="table-results" id="table_results_{g.group_id}">'
            f"<thead><tr>{header_ths}</tr></thead>"
            f"<tbody>{''.join(body_rows)}</tbody>"
            f"</table></div>"
        )

    return f"<html><body>{''.join(tables)}</body></html>"
