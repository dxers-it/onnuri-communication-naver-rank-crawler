import logging, os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

__version__ = os.getenv('VERSION')

logger = logging.getLogger('crawler')
logger.setLevel(logging.INFO)
logger.propagate = False

_formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    _console_handler = logging.StreamHandler()
    _console_handler.setLevel(logging.INFO)
    _console_handler.setFormatter(_formatter)
    logger.addHandler(_console_handler)

ROOT_DIR = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT_DIR / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)

if not any(isinstance(h, (TimedRotatingFileHandler, logging.FileHandler)) for h in logger.handlers):
    log_file = LOG_DIR / 'crawler.log'
    _file_handler = TimedRotatingFileHandler(
        filename=log_file,
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8',
        utc=False,
    )
    _file_handler.suffix = '%Y%m%d'
    _file_handler.setLevel(logging.INFO)
    _file_handler.setFormatter(_formatter)
    logger.addHandler(_file_handler)

logger.info(f'Initializing crawler package (version {__version__})')
logger.info(f'Logging to: {(LOG_DIR / 'crawler.log').as_posix()}')
