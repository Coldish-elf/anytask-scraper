# Project architecture

## Purpose

The project collects data from `anytask.org` and provides three interfaces:

1. CLI (`anytask-scraper`)
2. TUI (`anytask-tui`)
3. Python API (`import anytask_scraper`)

## Layers

### 1. Transport (`client.py`)

`AnytaskClient` is responsible for HTTP:

- login via Django form with CSRF
- storage of cookies
- re-authorization in case of expired session
- loading HTML pages and AJAX JSON
- downloading files and Colab notebook.

### 2. Parsing (`parser.py`)

Converts HTML into typed models (`dataclass`).

Key entrances:

- course page
- queue page
- issue page
- statement page
- profile page.

### 3. Models (`models.py`)

Defines the application data structure:

- course/task
- queue/comments/attachments
- statement by groups
- filtering functions (`filter_gradebook`, range of surnames).

### 4. Storage (`storage.py`)

Exports models to `JSON` / `CSV` / `Markdown` and downloads submissions files.

Additional state layer: `json_db.py` with `QueueJsonDB` for local JSON database
queues (`courses -> students -> assignments -> files`) and `issue_chain` write/grade event log.

### 5. Display (`display.py`)

Renders Rich tables and panels in the terminal for the CLI.

### 6. CLI orchestrator (`cli.py`)

Connects all levels:

- parses arguments
- applies settings
- performs authorization
- runs scripts `discover/course/queue/gradebook`
- writes export and/or prints tables.

### 7. TUI (`tui/*`)

`Textual`-application for interactive work:

- login screen
- main screen with tabs
- submission screen
- context action menu
- filters, export preview, copy-to-clipboard.

## Data flow

Typical flow:

1. `client` downloads HTML/JSON.
2. `parser` turns the input into `dataclass` objects.
3. `models` apply filters/normalization.
4. `storage` saves the result to disk.
5. `display`/TUI shows data to the user.

## Entry points

- CLI entrypoint: `anytask_scraper.cli:main`
- TUI entrypoint: `anytask_scraper.tui:run`
- Library: `anytask_scraper/__init__.py` (public API export)

## State files

- `.anytask_scraper_settings.json` - CLI/TUI settings.
- `credentials.json` - login/password.
- `.anytask_session.json` - session cookie.
- `~/.config/anytask-scraper/courses.json` - saved list of courses in TUI.
