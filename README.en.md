# Anytask Scraper

anytask-scraper is a CLI, TUI, and Python library for [anytask.org](https://anytask.org/).

## Requirements

Python `3.10+` is required.

## Installation

```bash
pip install git+https://github.com/Coldish-elf/anytask_scraper.git
```

With HTTP API support:

```bash
pip install "anytask-scraper[api] @ git+https://github.com/Coldish-elf/anytask_scraper.git"
```

or

```bash
git clone https://github.com/Coldish-elf/anytask_scraper.git
cd anytask_scraper
pip install -e .
```

## Quick check

```bash
anytask-scraper -h
# or quick TUI start
anytask-tui
```

## Basic CLI workflow

1. Initialize settings:

```bash
anytask-scraper settings init
```

2. Fill in `credentials.json` (login/password).

3. Fetch course data:

```bash
anytask-scraper course -c 12345 --show
```

4. Fetch the review queue:

```bash
anytask-scraper queue -c 12345 --show
```

5. Use local JSON DB for queue entries (optional):

```bash
anytask-scraper db sync -c 12345 --db-file ./output/queue_db.json --pull --limit 20 -f table
anytask-scraper db pull -c 12345 --db-file ./output/queue_db.json \
  --student-contains alice --status-contains review --issue-id 421525 -f table
```

## Documentation

- [Quick Start](docs-en/QuickStart.md)
- [CLI](docs-en/CLI.md)
- [TUI](docs-en/TUI.md)
- [HTTP API](docs-en/API.md)
- [Configuration](docs-en/Configuration.md)
- [Export Formats](docs-en/Export_Formats.md)
- [Architecture](docs-en/Architecture.md)
- [Library Reference](docs-en/Library_Reference.md)
- [Changelog](docs-en/Changelog.md)
