import logging
from logging.handlers import RotatingFileHandler
from utils import get_user_dir


_FILE_RELATIVE_PATH = 'log/log'
_FILE_MAX_BYTES = 5 * 1024 * 1024
_FILE_FORMATTER = logging.Formatter(
    fmt='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
    datefmt='%Y.%m.%d %H:%M:%S',
)

_CONSOLE_FORMATTER = logging.Formatter(
    fmt='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
    datefmt='%H:%M:%S',
)


def init(*, clevel='INFO', flevel='INFO'):
    console_handler = _create_console_handler(clevel)
    file_handler = _create_file_handler(_FILE_RELATIVE_PATH, flevel)

    _init_logger(logging.getLogger(), [console_handler, file_handler])


def _create_console_handler(level):
    handler = logging.StreamHandler()
    handler.setLevel(level.upper())
    handler.setFormatter(_CONSOLE_FORMATTER)
    return handler


def _create_file_handler(file_relative_path, level):
    file_path = get_user_dir() / file_relative_path
    file_path.parent.mkdir(parents=True, exist_ok=True)

    handler = RotatingFileHandler(
        file_path,
        maxBytes=_FILE_MAX_BYTES,
        backupCount=10,
        encoding='utf-8',
    )
    handler.setLevel(level.upper())
    handler.setFormatter(_FILE_FORMATTER)
    return handler


def _init_logger(logger, handlers, *, propagate=False):
    logger.setLevel(logging.DEBUG)
    logger.propagate = propagate
    for handler in handlers:
        logger.addHandler(handler)
