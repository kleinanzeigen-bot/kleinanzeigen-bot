"""
SPDX-FileCopyrightText: © Sebastian Thomschke and contributors
SPDX-License-Identifier: AGPL-3.0-or-later
SPDX-ArtifactOfProjectHomePage: https://github.com/Second-Hand-Friends/kleinanzeigen-bot/
"""
import copy, logging, re, sys
from gettext import gettext as _
from logging.handlers import RotatingFileHandler
from typing import Any, Final  # @UnusedImport

import colorama
from . import i18n, reflect

__all__ = [
    "Logger",
    "LogFileHandle",
    "DEBUG",
    "INFO",
    "configure_console_logging",
    "configure_file_logging",
    "flush_all_handlers",
    "get_logger",
    "is_debug"
]

Logger = logging.Logger
DEBUG:Final[int] = logging.DEBUG
INFO:Final[int] = logging.INFO

LOG_ROOT:Final[logging.Logger] = logging.getLogger()


def configure_console_logging() -> None:

    class CustomFormatter(logging.Formatter):
        LEVEL_COLORS = {
            logging.DEBUG: colorama.Fore.BLACK + colorama.Style.BRIGHT,
            logging.INFO: colorama.Fore.BLACK + colorama.Style.BRIGHT,
            logging.WARNING: colorama.Fore.YELLOW,
            logging.ERROR: colorama.Fore.RED,
            logging.CRITICAL: colorama.Fore.RED,
        }
        MESSAGE_COLORS = {
            logging.DEBUG: colorama.Fore.BLACK + colorama.Style.BRIGHT,
            logging.INFO: colorama.Fore.RESET,
            logging.WARNING: colorama.Fore.YELLOW,
            logging.ERROR: colorama.Fore.RED,
            logging.CRITICAL: colorama.Fore.RED + colorama.Style.BRIGHT,
        }
        VALUE_COLORS = {
            logging.DEBUG: colorama.Fore.BLACK + colorama.Style.BRIGHT,
            logging.INFO: colorama.Fore.MAGENTA,
            logging.WARNING: colorama.Fore.MAGENTA,
            logging.ERROR: colorama.Fore.MAGENTA,
            logging.CRITICAL: colorama.Fore.MAGENTA,
        }

        def format(self, record:logging.LogRecord) -> str:
            record = copy.deepcopy(record)

            level_color = self.LEVEL_COLORS.get(record.levelno, "")
            msg_color = self.MESSAGE_COLORS.get(record.levelno, "")
            value_color = self.VALUE_COLORS.get(record.levelno, "")

            # translate and colorize log level name
            levelname = _(record.levelname) if record.levelno > logging.DEBUG else record.levelname
            record.levelname = f"{level_color}[{levelname}]{colorama.Style.RESET_ALL}"

            # highlight message values enclosed by [...], "...", and '...'
            record.msg = re.sub(
                r"\[([^\]]+)\]|\"([^\"]+)\"|\'([^\']+)\'",
                lambda match: f"[{value_color}{match.group(1) or match.group(2) or match.group(3)}{colorama.Fore.RESET}{msg_color}]",
                str(record.msg),
            )

            # colorize message
            record.msg = f"{msg_color}{record.msg}{colorama.Style.RESET_ALL}"

            return super().format(record)

    formatter = CustomFormatter("%(levelname)s %(message)s")

    stdout_log = logging.StreamHandler(sys.stderr)
    stdout_log.setLevel(logging.DEBUG)
    stdout_log.addFilter(type("", (logging.Filter,), {
        "filter": lambda rec: rec.levelno <= logging.INFO
    }))
    stdout_log.setFormatter(formatter)
    LOG_ROOT.addHandler(stdout_log)

    stderr_log = logging.StreamHandler(sys.stderr)
    stderr_log.setLevel(logging.WARNING)
    stderr_log.setFormatter(formatter)
    LOG_ROOT.addHandler(stderr_log)


class LogFileHandle:
    """Encapsulates a log file handler with close and status methods."""

    def __init__(self, file_path: str, handler: RotatingFileHandler, logger: logging.Logger):
        self.file_path = file_path
        self._handler:RotatingFileHandler | None = handler
        self._logger = logger

    def close(self) -> None:
        """Flushes, removes, and closes the log handler."""
        if self._handler:
            self._handler.flush()
            self._logger.removeHandler(self._handler)
            self._handler.close()
            self._handler = None

    def is_closed(self) -> bool:
        """Returns whether the log handler has been closed."""
        return not self._handler


def configure_file_logging(log_file_path:str) -> LogFileHandle:
    """
    Sets up a file logger and returns a callable to flush, remove, and close it.

    @param log_file_path: Path to the log file.
    @return: Callable[[], None]: A function that cleans up the log handler.
    """
    fh = RotatingFileHandler(
        filename = log_file_path,
        maxBytes = 10 * 1024 * 1024,  # 10 MB
        backupCount = 10,
        encoding = "utf-8"
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    LOG_ROOT.addHandler(fh)
    return LogFileHandle(log_file_path, fh, LOG_ROOT)


def flush_all_handlers() -> None:
    for handler in LOG_ROOT.handlers:
        handler.flush()


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Returns a localized logger
    """

    class TranslatingLogger(logging.Logger):

        def _log(self, level: int, msg: object, *args: Any, **kwargs: Any) -> None:
            if level != logging.DEBUG:  # debug messages should not be translated
                msg = i18n.translate(msg, reflect.get_caller(2))
            super()._log(level, msg, *args, **kwargs)

    logging.setLoggerClass(TranslatingLogger)
    return logging.getLogger(name)


def is_debug(logger:Logger) -> bool:
    return logger.isEnabledFor(logging.DEBUG)
