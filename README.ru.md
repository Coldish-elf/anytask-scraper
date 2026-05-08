# Anytask Scraper

[![CI](https://github.com/Coldish-elf/anytask-scraper/actions/workflows/ci.yml/badge.svg)](https://github.com/Coldish-elf/anytask-scraper/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

[English](README.md)

`anytask-scraper` - Python-инструментарий для работы с [anytask.org](https://anytask.org/). В репозитории есть:

- CLI
- TUI для интерактивной навигации
- опциональный HTTP API для локальной автоматизации
- Python-библиотека для скриптов и интеграций

## Требования

- Python `3.10+`

## Установка

Только библиотека:

```bash
pip install "git+https://github.com/Coldish-elf/anytask-scraper.git"
```

С CLI и TUI:

```bash
pip install "anytask-scraper[tui] @ git+https://github.com/Coldish-elf/anytask-scraper.git"
```

С HTTP API сервером:

```bash
pip install "anytask-scraper[tui,api] @ git+https://github.com/Coldish-elf/anytask-scraper.git"
```

Для локальной разработки:

```bash
git clone https://github.com/Coldish-elf/anytask-scraper.git
cd anytask-scraper
pip install -e ".[dev,api]"
```

## Быстрый старт

Инициализируйте и заполните шаблон учетных данных:

```bash
anytask-scraper settings init
```

Проверьте CLI:

```bash
anytask-scraper -h
```

Получите краткую сводку по условному курсу:

```bash
anytask-scraper course -c 12345 --show
```

Получите очередь на проверку:

```bash
anytask-scraper queue -c 12345 --show
```

Запустите TUI:

```bash
anytask-tui
```

Запустите HTTP API:

```bash
anytask-api
```

## Документация

English:

- [Quick Start](docs-en/QuickStart.md)
- [CLI](docs-en/CLI.md)
- [TUI](docs-en/TUI.md)
- [HTTP API](docs-en/API.md)
- [Configuration](docs-en/Configuration.md)
- [Export Formats](docs-en/Export_Formats.md)
- [Architecture](docs-en/Architecture.md)
- [Library Reference](docs-en/Library_Reference.md)

Русский:

- [Быстрый старт](docs-ru/QuickStart.md)
- [CLI](docs-ru/CLI.md)
- [TUI](docs-ru/TUI.md)
- [HTTP API](docs-ru/API.md)
- [Конфигурация](docs-ru/Configuration.md)
- [Форматы экспорта](docs-ru/Export_Formats.md)
- [Архитектура](docs-ru/Architecture.md)
- [Справочник библиотеки](docs-ru/Library_Reference.md)
