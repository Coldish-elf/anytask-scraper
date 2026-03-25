from __future__ import annotations

import logging
from pathlib import Path

DEFAULT_FORMAT = "%(asctime)s %(name)s %(levelname)s %(message)s"


def setup_logging(
    level: int = logging.WARNING,
    log_file: str | None = None,
    fmt: str = DEFAULT_FORMAT,
) -> None:
    root_logger = logging.getLogger("anytask_scraper")
    root_logger.setLevel(level)

    if root_logger.handlers:
        root_logger.handlers.clear()

    formatter = logging.Formatter(fmt)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)

    if log_file:
        path = Path(log_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(str(path), encoding="utf-8")
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
