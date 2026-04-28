from __future__ import annotations

import logging
import sys
from pathlib import Path


LOGS_DIR = Path("logs")
LOG_FILE = LOGS_DIR / "argos.log"


def setup_logging(level: str = "INFO") -> logging.Logger:
    LOGS_DIR.mkdir(exist_ok=True)

    numeric_level = getattr(logging, level.upper(), logging.INFO)

    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Reduce ruido de librerías externas.
    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("discord.gateway").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    return logging.getLogger("ARGOS")


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"ARGOS.{name}")
