import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(name: str = __name__,
                 log_file: str = None,
                 level: int = logging.INFO,
                 max_bytes: int = 5 * 1024 * 1024,  # 5 MB
                 backup_count: int = 5) -> logging.Logger:
    """
    Logger s rotáciou log súborov.

    :param name: Názov loggera
    :param log_file: Cesta k log súboru
    :param level: Úroveň logovania (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    :param max_bytes: Maximálna veľkosť log súboru pred rotáciou
    :param backup_count: Počet záložných súborov, ktoré sa uchovajú
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger  # Zabráni duplicitným handlerom

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler pre konzolu
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Uistíme sa, že adresár pre logy existuje
    os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)

    # Rotujúci file handler
    rotating_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8"
    )
    rotating_handler.setFormatter(formatter)
    logger.addHandler(rotating_handler)

    return logger


# --- Použitie ---
if __name__ == "__main__":
    log = setup_logger(
        name="MyApp",
        log_file="logs/app.log",
        level=logging.DEBUG,
        max_bytes=1024 * 1024,  # 1 MB
        backup_count=3
    )