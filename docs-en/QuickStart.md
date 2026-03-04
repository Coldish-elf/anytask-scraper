# Quick start

## 1. Installation

```bash
pip install git+https://github.com/Coldish-elf/anytask_scraper.git
```

For development:

```bash
git clone https://github.com/Coldish-elf/anytask_scraper.git
cd anytask_scraper
pip install -e ".[dev]"
```

Examination:

```bash
anytask-scraper -h
```

## 2. Initializing settings

```bash
anytask-scraper settings init
```

The team creates:

- `.anytask_scraper_settings.json` - default settings file
- `credentials.json` - login/password template (if there was no file).

## 3. Filling in credentials

Fill out `credentials.json`:

```json
{
  "username": "your_login",
  "password": "your_password"
}
```

Other file formats are also supported (`key=value`, `key:value`, two lines `username`/`password`), more details in [Configuration](Configuration.md).

## 4. First export of the course

```bash
anytask-scraper course -c 12345 -f json -o ./output --show
```

What will happen:

- you will be logged in to Anytask
- the course page `12345` will be loaded
- data will be saved in `./output/course_12345.json`
- the table will be shown in the terminal.

## 5. Teacher's turn

```bash
anytask-scraper queue -c 12345 --deep -f markdown -o ./output
```

`--deep` additionally loads issue pages and comments.

## 6. Statement

```bash
anytask-scraper gradebook -c 12345 -f csv -o ./output
```

## 7. Auto-detection of courses

```bash
anytask-scraper discover
```

## 8. Launch TUI

```bash
anytask-tui
anytask-scraper tui
```

Then use the [TUI](TUI.md) manual.
