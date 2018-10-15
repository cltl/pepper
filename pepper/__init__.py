import logging
import os


# Global Logging Setup
LOGGING_LEVEL = logging.DEBUG
LOGGING_FILE = 'log.txt'
LOGGING_FORMAT = '%(asctime)s %(levelname)-8s %(name)-35s %(message)s'
LOGGING_DATE_FORMAT = '%x %X'

LOGGING_LEVEL_CONSOLE = LOGGING_LEVEL
LOGGING_FORMAT_CONSOLE = '\r%(asctime)s %(levelname)-8s %(name)-35s %(message)s'
LOGGING_DATE_FORMAT_CONSOLE = LOGGING_DATE_FORMAT

logging.basicConfig(level=LOGGING_LEVEL, format=LOGGING_FORMAT, datefmt=LOGGING_DATE_FORMAT,
                    filename=os.path.join(os.path.dirname(__file__), LOGGING_FILE))

console_logger = logging.StreamHandler()
console_logger.setLevel(LOGGING_LEVEL_CONSOLE)
console_logger.setFormatter(logging.Formatter(LOGGING_FORMAT_CONSOLE, LOGGING_DATE_FORMAT_CONSOLE))
logger = logging.getLogger("pepper")

logger.addHandler(console_logger)

# Set GOOGLE CREDENTIALS
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.path.dirname(__file__), "../google_cloud_key.json")
