# Anytask Scraper

anytask-scraper - CLI, TUI и Python-библиотека для [anytask.org](https://anytask.org/).

## Требования

Нужен Python `3.10+`.

## Установка

```bash
pip install git+https://github.com/Coldish-elf/anytask_scraper.git
```

С поддержкой HTTP API:

```bash
pip install "anytask-scraper[api] @ git+https://github.com/Coldish-elf/anytask_scraper.git"
```

Или

```bash
git clone https://github.com/Coldish-elf/anytask_scraper.git
cd anytask_scraper
pip install -e .
```

## Быстрая проверка

```bash
anytask-scraper -h
# или быстрый старт TUI
anytask-tui
# или быстрый старт API
anytask-api
```

## Базовый сценарий CLI

1. Инициализируйте настройки:

```bash
anytask-scraper settings init
```

2. Заполните `credentials.json` (логин/пароль).

3. Получите данные по курсу:

```bash
anytask-scraper course -c 12345 --show
```

4. Получите очередь:

```bash
anytask-scraper queue -c 12345 --show
```

5. Локальная JSON DB очереди (опционально):

```bash
anytask-scraper db sync -c 12345 --db-file ./output/queue_db.json --pull --limit 20 -f table
anytask-scraper db pull -c 12345 --db-file ./output/queue_db.json \
  --student-contains alice --status-contains review --issue-id 421525 -f table
```

## Документация

- [Быстрый старт](docs/QuickStart.md)
- [CLI](docs/CLI.md)
- [TUI](docs/TUI.md)
- [HTTP API](docs/API.md)
- [Конфигурация](docs/Configuration.md)
- [Форматы экспорта](docs/Export_Formats.md)
- [Архитектура](docs/Architecture.md)
- [Справочник библиотеки](docs/Library_Reference.md)
- [Roadmap](docs/roadmap.md)
- [Changelog](docs/Changelog.md)
