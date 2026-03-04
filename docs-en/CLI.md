# CLI

Main command:

```bash
anytask-scraper
```

## General syntax

```bash
anytask-scraper [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]
```

## Global options

These options can be used with any subcommand.

| Option | Destination |
| --- | --- |
| `-u`, `--username` | Anytask login. |
| `-p`, `--password` | Anytask password. |
| `--credentials-file` | Path to the credentials file (`json`, `key=value`, `key:value`, or 2 lines). |
| `--session-file` | Path to the session cookie. |
| `--status-mode all\|errors` | Show all status messages or only errors. |
| `--default-output` | Base export folder (`course`, `queue`, `gradebook`). |
| `--save-session`, `--no-save-session` | Enable/disable session saving after command execution. |
| `--refresh-session`, `--no-refresh-session` | Ignore the saved session and login again. |
| `--settings-file` | Path to the user settings JSON file. |
| `-d`, `--debug` | Enable debug logging. |
| `--log-file` | Path to the log file. |

## `tui` command

Launches a text interface:

```bash
anytask-scraper tui
anytask-tui
```

## `discover` command

Reads the user's profile and displays available courses with roles.

```bash
anytask-scraper discover [--role all|student|teacher] [--student-only]
```

Options:

| Option | Destination |
| --- | --- |
| `--role all\|student\|teacher` | Filter by role (default `all`). |
| `--student-only` | Leaves only courses where the user is a student and not a teacher of the same course. |

## `course` command

Loads tasks for a course (or several courses).

```bash
anytask-scraper course -c COURSE_ID [COURSE_ID ...] [OPTIONS]
```

Options:

| Option | Destination |
| --- | --- |
| `-c`, `--course` | One or more course IDs. |
| `-o`, `--output` | Output folder. |
| `--filename` | Export file name (with or without extension). For several `--course` is not available. |
| `-f`, `--format json\|markdown\|csv\|table` | Output format. `table` only prints the table, no file is created. |
| `--show` | After export, show the table in the terminal. |
| `--fetch-descriptions` | For teacher-view, it loads full task descriptions via `/task/edit/{id}`. |
| `--include-columns` | Export only the listed columns. |
| `--exclude-columns` | Exclude the listed columns. |

Supported columns depend on the course view:

- student-view: `#`, `Title`, `Score`, `Status`, `Deadline`
- teacher-view: `#`, `Title`, `Section`, `Max Score`, `Deadline`.

## `queue` command

Loads the course check queue.

```bash
anytask-scraper queue -c COURSE_ID [OPTIONS]
```

Options:

| Option | Destination |
| --- | --- |
| `-c`, `--course` | Course ID. |
| `-o`, `--output` | Output folder. |
| `--filename` | Export file name. |
| `-f`, `--format json\|markdown\|csv\|table` | Output format (`table` without file writing). |
| `--show` | After export, show the table in the terminal. |
| `--deep` | For each available entry, loads the issue page and collects `Submission`. |
| `--download-files` | Downloads files from comments and Colab links automatically includes `--deep`. |
| `--filter-task` | Filter by task name substring. |
| `--filter-reviewer` | Filter by substring of the reviewer name. |
| `--filter-status` | Filter by status substring. |
| `--last-name-from` | Last name lower border filter (case insensitive). |
| `--last-name-to` | Last name upper border filter (prefix-inclusive). |
| `--include-columns` | Export only the listed columns. |
| `--exclude-columns` | Exclude the listed columns. |

Queue columns: `#`, `Student`, `Task`, `Status`, `Reviewer`, `Updated`, `Grade`.

Additionally, with `-f csv` and `--deep` the file `submissions_{course_id}.csv` is created.

## `gradebook` command

Loads the course transcript.

```bash
anytask-scraper gradebook -c COURSE_ID [OPTIONS]
```

Options:

| Option | Destination |
| --- | --- |
| `-c`, `--course` | Course ID. |
| `-o`, `--output` | Output folder. |
| `--filename` | Export file name. |
| `-f`, `--format json\|markdown\|csv\|table` | Output format (`table` without file writing). |
| `--show` | After export, show the table in the terminal. |
| `--filter-group` | Filter by substring of the group name (case insensitive). |
| `--filter-student` | Filter by substring of student name (case insensitive). |
| `--filter-teacher` | Filter by the exact name of the group teacher. |
| `--min-score` | Leave students with a score of `>=` values. |
| `--last-name-from` | The lower limit of the range of surnames. |
| `--last-name-to` | The upper limit of the range of surnames. |
| `--include-columns` | Export only the listed columns. |
| `--exclude-columns` | Exclude the listed columns. |

Columns: `Group`, `Student`, dynamic set of tasks, `Total`.

## `db` command

Local JSON base for a queue with hierarchy:
`courses -> students -> assignments -> files` + `issue_chain`.

```bash
anytask-scraper db sync -c COURSE_ID [OPTIONS]
anytask-scraper db pull [OPTIONS]
anytask-scraper db process -c COURSE_ID --student-key KEY --assignment-key KEY [OPTIONS]
anytask-scraper db write -c COURSE_ID --issue-id ISSUE_ID --action ACTION --value VALUE [OPTIONS]
```

### `db sync`

Loads the course queue and syncs the DB.

Options:

| Option | Destination |
| --- | --- |
| `-c`, `--course` | Course ID. |
| `--db-file` | Path to JSON DB (default `./queue_db.json`). |
| `--course-title` | Explicit course title for saving in DB. |
| `--deep` | Loads issue pages and writes comments to `issue_chain`. |
| `--filter-task` | Filter by task. |
| `--filter-reviewer` | Filter by reviewer. |
| `--filter-status` | Filter by status. |
| `--last-name-from` | The lower limit of the surname. |
| `--last-name-to` | The upper limit of the surname. |
| `--pull` | Immediately after sync, pull new records. |
| `--limit` | Limit the number of entries with `--pull`. |
| `--student-contains` | With `--pull`: pull only by substring in the student name (case insensitive). |
| `--task-contains` | With `--pull`: pull only by substring in the task name (case insensitive). |
| `--status-contains` | With `--pull`: pull only by substring in the status (case insensitive). |
| `--reviewer-contains` | With `--pull`: pull only by substring in the reviewer name (case insensitive). |
| `--pull-last-name-from` | With `--pull`: the lower limit of the last name range. |
| `--pull-last-name-to` | With `--pull`: the upper limit of the range of surnames. |
| `--issue-id` | With `--pull`: pull only for a specific `issue_id`. |
| `-f`, `--format json\|table` | Output format of pulled records with `--pull`. |

### `db pull`

Pulls `queue_state == new` entries and marks them as `pulled`.

Options:

| Option | Destination |
| --- | --- |
| `--db-file` | Path to JSON DB. |
| `-c`, `--course` | Optionally limit to a specific course. |
| `--limit` | Limit the number of pulled records. |
| `--student-contains` | Pull only by substring in the student's name (case insensitive). |
| `--task-contains` | Pull only by substring in the task name (case insensitive). |
| `--status-contains` | Pull only by substring in the status (case insensitive). |
| `--reviewer-contains` | Pull only by substring in the reviewer name (case insensitive). |
| `--last-name-from` | The lower limit of the range of surnames. |
| `--last-name-to` | The upper limit of the range of surnames. |
| `--issue-id` | Pull only on a specific `issue_id`. |
| `-f`, `--format json\|table` | Output format. |

### `db process`

Marks the pulled entry as `processed`.

Options:

| Option | Destination |
| --- | --- |
| `--db-file` | Path to JSON DB. |
| `-c`, `--course` | Course ID. |
| `--student-key` | `student_key` from `db pull`. |
| `--assignment-key` | `assignment_key` from `db pull`. |

### `db write`

Adds a write event to `issue_chain` (for example grading/status update).

Options:

| Option | Destination |
| --- | --- |
| `--db-file` | Path to JSON DB. |
| `-c`, `--course` | Course ID. |
| `--issue-id` | Issue ID. |
| `--action` | Action type (`grade`, `status`, `reviewer`, ...). |
| `--value` | New meaning. |
| `--author` | Who performed the action. |
| `--note` | Additional note. |

## `serve` command

Launches the HTTP API server (FastAPI + uvicorn).

```bash
anytask-scraper serve [OPTIONS]
```

Options:

| Option | Destination |
| --- | --- |
| `--host` | Host for bind (default `127.0.0.1`). |
| `--port` | Port for bind (default `8000`). |
| `--session-file` | Optional session file to load at startup. |
| `--reload` | Enable auto-restart in development mode. |

Notes:

- API dependencies required: `pip install "anytask-scraper[api]"`.
- With `--reload` uvicorn is launched in factory mode via import string.

## `settings` command

Manages the local settings file.

```bash
anytask-scraper settings init
anytask-scraper settings show
anytask-scraper settings set [OPTIONS]
anytask-scraper settings clear [KEY ...]
```

`settings set` options:

- `--credentials-file`
- `--session-file`
- `--status-mode all|errors`
- `--default-output`
- `--save-session / --no-save-session`
- `--refresh-session / --no-refresh-session`
- `--auto-login-session / --no-auto-login-session`
- `--debug / --no-debug`

Keys for `settings clear`: `credentials_file`, `session_file`, `status_mode`, `default_output`, `save_session`, `refresh_session`, `auto_login_session`, `debug`.

## Errors and exit codes

The CLI terminates the process with code `1` for authorization errors, settings reading errors, argument validation errors, and network errors.

## Examples

```bash
anytask-scraper discover

anytask-scraper course -c 11111 22222 -f csv -o ./output

anytask-scraper queue -c 11111 --download-files -o ./output

anytask-scraper gradebook -c 11111 --filter-group IDK --min-score 50 -f markdown

anytask-scraper db sync -c 11111 --db-file ./output/queue_db.json --pull --limit 10 -f table

anytask-scraper db pull --db-file ./output/queue_db.json -c 11111 \
  --student-contains alice --task-contains "hw 1" \
  --status-contains review --reviewer-contains bob \
  --last-name-from a --last-name-to s --issue-id 421525 -f table

anytask-scraper db process -c 11111 --db-file ./output/queue_db.json \
  --student-key /users/alice/ --assignment-key issue:421525

anytask-scraper db write -c 11111 --db-file ./output/queue_db.json \
  --issue-id 421525 --action grade --value "10/10" --author "Bob"
```
