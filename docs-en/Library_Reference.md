# Library API

`anytask-scraper` can be used as a Python package:

```python
from anytask_scraper import AnytaskClient, parse_course_page
```

## Quick example

```python
from anytask_scraper import (
    AnytaskClient,
    extract_csrf_from_queue_page,
    parse_course_page,
    parse_submission_page,
    save_course_json,
)

with AnytaskClient(username="login", password="password") as client:
    course_html = client.fetch_course_page(12345)
    course = parse_course_page(course_html, 12345)
    save_course_json(course, "./output")

    queue_html = client.fetch_queue_page(12345)
    csrf = extract_csrf_from_queue_page(queue_html)
    rows = client.fetch_all_queue_entries(12345, csrf)

    if rows:
        issue_url = str(rows[0].get("issue_url", ""))
        if issue_url:
            sub_html = client.fetch_submission_page(issue_url)
            submission = parse_submission_page(sub_html, issue_id=1)
            print(submission.task_title)
```

## Client

### `AnytaskClient`

Creates an HTTP client with support for login, session cookies and automatic re-login in case of a failed session.

Constructor:

```python
AnytaskClient(username: str = "", password: str = "")
```

Public methods:

| Method | Destination |
| --- | --- |
| `login()` | Performs login via a Django form (`/accounts/login/`). |
| `load_session(session_path)` | Loads cookies from JSON, returns `True/False`. |
| `save_session(session_path)` | Saves the current cookies to a JSON file. |
| `fetch_course_page(course_id)` | Returns the HTML of the course page. |
| `fetch_profile_page()` | Returns the HTML of the user's profile page. |
| `fetch_task_description(task_id)` | Returns the HTML description of the task from `/task/edit/{id}`. |
| `fetch_queue_page(course_id)` | Returns the HTML of the course queue page. |
| `fetch_gradebook_page(course_id)` | Returns the HTML of the course statement page. |
| `fetch_queue_ajax(course_id, csrf_token, start=0, length=50, filter_query="")` | Reads one page of the AJAX queue. |
| `fetch_all_queue_entries(course_id, csrf_token, filter_query="")` | Reads the entire queue with pagination. |
| `fetch_submission_page(issue_url)` | Returns HTML issue (full URL or relative path). |
| `download_file(url, output_path)` | Downloads the file and validates the content. |
| `download_colab_notebook(colab_url, output_path)` | Trying to download Colab notebook as `.ipynb`. |
| `close()` | Closes the HTTP client. |
| `__enter__()` / `__exit__()` | Context manager support. |

Exceptions and results:

- `LoginError` - authorization error.
- `DownloadResult(success: bool, path: str, reason: str = "")` - download result.

Typical `DownloadResult.reason`:
`ok`, `download_error`, `login_redirect`, `html_instead_of_file`, `invalid_notebook_format`, `google_drive_html_page`, `no_file_id_in_url`.

## Parsers

### `parse_course_page(html, course_id) -> Course`

Parses the course page, automatically supports student-view and teacher-view.

### `parse_profile_page(html) -> list[ProfileCourseEntry]`

Reads the profile and returns the courses of the user with the role `teacher`/`student`.

### `parse_gradebook_page(html, course_id) -> Gradebook`

Parses score sheets by group, task, and student.

### `parse_submission_page(html, issue_id) -> Submission`

Parses the issue page: metadata, comments, files, links, deadline flags.

### `parse_queue_filters(html) -> QueueFilters`

Retrieves available filter options from a queue modal window.

### Auxiliary functions

| Function | Destination |
| --- | --- |
| `parse_task_edit_page(html) -> str` | Extract the task description from the edit page. |
| `strip_html(text) -> str` | Clean up HTML to plain text with line breaks. |
| `extract_csrf_from_queue_page(html) -> str` | Get a CSRF token for the AJAX queue. |
| `extract_issue_id_from_breadcrumb(html) -> int` | Extract numeric issue ID from breadcrumb. |
| `format_student_folder(name) -> str` | Convert student name to folder name. |

## Data models

### Course and objectives

`Task`:

- `task_id: int`
- `title: str`
- `description: str = ""`
- `deadline: datetime | None = None`
- `max_score: float | None = None`
- `score: float | None = None`
- `status: str = ""`
- `section: str = ""`
- `edit_url: str = ""`
- `submit_url: str = ""`

`Course`:

- `course_id: int`
- `title: str = ""`
- `teachers: list[str]`
- `tasks: list[Task]`

`ProfileCourseEntry`:

- `course_id: int`
- `title: str`
- `role: str`

### Queue and decisions

`QueueEntry`:

- `student_name`, `student_url`, `task_title`, `update_time`, `mark`
- `status_color`, `status_name`
- `responsible_name`, `responsible_url`
- `has_issue_access: bool`
- `issue_url`

`FileAttachment`:

- `filename: str`
- `download_url: str`
- `is_notebook: bool = False`

`Comment`:

- `author_name`, `author_url`
- `timestamp: datetime | None`
- `content_html: str`
- `files: list[FileAttachment]`
- `links: list[str]`
- `is_after_deadline: bool`
- `is_system_event: bool`

`Submission`:

- `issue_id: int`
- `task_title: str`
- `student_name`, `student_url`
- `reviewer_name`, `reviewer_url`
- `status`, `grade`, `max_score`, `deadline`
- `comments: list[Comment]`

`QueueFilters`:

- `students: list[tuple[value, label]]`
- `tasks: list[tuple[value, label]]`
- `reviewers: list[tuple[value, label]]`
- `statuses: list[tuple[value, label]]`

`ReviewQueue`:

- `course_id: int`
- `entries: list[QueueEntry]`
- `submissions: dict[str, Submission]` (key - `issue_url`)

### Statement

`GradebookEntry`:

- `student_name`, `student_url`
- `scores: dict[task_title, float]`
- `statuses: dict[task_title, str]`
- `issue_urls: dict[task_title, str]`
- `total_score: float`

`GradebookGroup`:

- `group_name: str`
- `group_id: int`
- `teacher_name: str`
- `task_titles: list[str]`
- `max_scores: dict[task_title, float]`
- `entries: list[GradebookEntry]`

`Gradebook`:

- `course_id: int`
- `groups: list[GradebookGroup]`

Model Features:

- `extract_last_name(name) -> str`
- `last_name_in_range(name, from_name="", to_name="") -> bool`
- `filter_gradebook(gradebook, group="", teacher="", student="", min_score=None, last_name_from="", last_name_to="") -> Gradebook`

## Export and save

### Course Features

| Function | Result |
| --- | --- |
| `save_course_json(course, output_dir=".", columns=None, filename=None)` | Path to `course_{id}.json`. |
| `save_course_markdown(course, output_dir=".", columns=None, filename=None)` | Path to `course_{id}.md`. |
| `save_course_csv(course, output_dir=".", columns=None, filename=None)` | Path to `course_{id}.csv`. |

### Queue functions

| Function | Result |
| --- | --- |
| `save_queue_json(queue, output_dir=".", columns=None, filename=None)` | Path to `queue_{id}.json`. |
| `save_queue_markdown(queue, output_dir=".", columns=None, filename=None)` | Path to `queue_{id}.md`. |
| `save_queue_csv(queue, output_dir=".", columns=None, filename=None)` | Path to `queue_{id}.csv`. |

### Submissions functions

| Function | Result |
| --- | --- |
| `save_submissions_json(submissions, course_id, output_dir=".", columns=None, filename=None)` | Path to `submissions_{id}.json`. |
| `save_submissions_markdown(submissions, course_id, output_dir=".", columns=None, filename=None)` | Path to `submissions_{id}.md`. |
| `save_submissions_csv(submissions, course_id, output_dir=".", columns=None, filename=None)` | Path to `submissions_{id}.csv`. |
| `download_submission_files(client, submission, base_dir)` | `dict[source, saved_path]` on downloaded artifacts. |

### Statement functions

| Function | Result |
| --- | --- |
| `save_gradebook_json(gradebook, output_dir=".", columns=None, filename=None)` | Path to `gradebook_{id}.json`. |
| `save_gradebook_markdown(gradebook, output_dir=".", columns=None, filename=None)` | Path to `gradebook_{id}.md`. |
| `save_gradebook_csv(gradebook, output_dir=".", columns=None, filename=None)` | Path to `gradebook_{id}.csv`. |

`columns` in export functions limits the set of fields in the output file.

## JSON DB for queue

`QueueJsonDB(path, autosave=True)` stores a local JSON database with a strict structure:

- `courses -> students -> assignments -> files`
- for each assignment there is an `issue_chain` (queue events, comments, system events, write operations).

Key methods:

- `sync_queue(queue, course_title="") -> int` - synchronizes `ReviewQueue` to the database, returns the number of new/updated assignments marked as `new`.
- `pull_new_entries(course_id=None, limit=None, student_contains="", task_contains="", status_contains="", reviewer_contains="", last_name_from="", last_name_to="", issue_id=None) -> list[dict]` - retrieves only suitable new assignments and atomically transfers them to the `pulled` state.
- `mark_entry_processed(course_id, student_key, assignment_key) -> bool` - transfers the entry to `processed`.
- `record_issue_write(course_id, issue_id, action, value, author="", note="") -> bool` - writes an action to `issue_chain` (for example grading/status update).
- `snapshot() -> dict` - a copy of the current JSON payload.
- `save()` - forced saving to disk.

Minimal example:

```python
from anytask_scraper import QueueJsonDB, ReviewQueue

db = QueueJsonDB("./output/queue_db.json")
queue = ReviewQueue(course_id=1250)
db.sync_queue(queue, course_title="Python")

batch = db.pull_new_entries(
    course_id=1250,
    limit=20,
    student_contains="alice",
    status_contains="review",
)
for item in batch:
    print(item["student_name"], item["task_title"])
    db.mark_entry_processed(
        course_id=item["course_id"],
        student_key=item["student_key"],
        assignment_key=item["assignment_key"],
    )
```

## Rendering to terminal (Rich)

| Function | Destination |
| --- | --- |
| `display_course(course, console=None)` | Course Objectives Table. |
| `display_task_detail(task, console=None)` | Details of one task. |
| `display_queue(queue, console=None)` | Queue table. |
| `display_submission(submission, console=None)` | Comment thread issue. |
| `display_gradebook(gradebook, console=None)` | Listing tables by group. |

## Logging

`setup_logging(level=logging.WARNING, log_file=None, fmt=DEFAULT_FORMAT)` configures the `anytask_scraper` package logger.

## Minimum working script: queue + submissions + files

```python
from anytask_scraper import (
    AnytaskClient,
    ReviewQueue,
    extract_csrf_from_queue_page,
    extract_issue_id_from_breadcrumb,
    parse_submission_page,
    save_queue_json,
    save_submissions_markdown,
    download_submission_files,
)

course_id = 12345

with AnytaskClient("login", "password") as client:
    queue_html = client.fetch_queue_page(course_id)
    csrf = extract_csrf_from_queue_page(queue_html)
    rows = client.fetch_all_queue_entries(course_id, csrf)

    queue = ReviewQueue(course_id=course_id)
    for row in rows:
        issue_url = str(row.get("issue_url", ""))
        if not issue_url:
            continue
        sub_html = client.fetch_submission_page(issue_url)
        issue_id = extract_issue_id_from_breadcrumb(sub_html)
        if issue_id == 0:
            continue
        submission = parse_submission_page(sub_html, issue_id)
        queue.submissions[issue_url] = submission
        download_submission_files(client, submission, "./downloads")

    save_queue_json(queue, "./output")
    save_submissions_markdown(queue.submissions, course_id, "./output")
```
