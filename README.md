# Anytask Scraper

[![CI](https://github.com/Coldish-elf/anytask_scraper/actions/workflows/ci.yml/badge.svg)](https://github.com/Coldish-elf/anytask_scraper/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

[Русский](README.ru.md)

`anytask-scraper` is a Python toolkit for working with [anytask.org](https://anytask.org/). It includes:

- a CLI
- a TUI for interactive browsing
- an optional HTTP API for local automation
- a Python library for scripting and integrations

## Requirements

- Python `3.10+`

## Installation

Library only:

```bash
pip install "git+https://github.com/Coldish-elf/anytask_scraper.git"
```

With CLI and TUI:

```bash
pip install "anytask-scraper[tui] @ git+https://github.com/Coldish-elf/anytask_scraper.git"
```

With HTTP API server:

```bash
pip install "anytask-scraper[tui,api] @ git+https://github.com/Coldish-elf/anytask_scraper.git"
```

For local development:

```bash
git clone https://github.com/Coldish-elf/anytask_scraper.git
cd anytask_scraper
pip install -e ".[dev,api]"
```

## Quick Start

Initialize settings and fill a credential template:

```bash
anytask-scraper settings init
```

Check the CLI:

```bash
anytask-scraper -h
```

Fetch a course summary with a placeholder course ID:

```bash
anytask-scraper course -c 12345 --show
```

Fetch the review queue:

```bash
anytask-scraper queue -c 12345 --show
```

Start the TUI:

```bash
anytask-tui
```

Start the HTTP API:

```bash
anytask-api
```

## Documentation

English:

- [Quick Start](docs-en/QuickStart.md)
- [CLI](docs-en/CLI.md)
- [TUI](docs-en/TUI.md)
- [HTTP API](docs-en/API.md)
- [Configuration](docs-en/Configuration.md)
- [Export Formats](docs-en/Export_Formats.md)
- [Architecture](docs-en/Architecture.md)
- [Library Reference](docs-en/Library_Reference.md)

Russian:

- [Быстрый старт](docs-ru/QuickStart.md)
- [CLI](docs-ru/CLI.md)
- [TUI](docs-ru/TUI.md)
- [HTTP API](docs-ru/API.md)
- [Конфигурация](docs-ru/Configuration.md)
- [Форматы экспорта](docs-ru/Export_Formats.md)
- [Архитектура](docs-ru/Architecture.md)
- [Справочник библиотеки](docs-ru/Library_Reference.md)
