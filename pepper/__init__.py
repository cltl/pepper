"""
This is the main repository for Pepper/Nao Applications created as part of the
Computational Lexicology & Terminology Lab (CLTL) at the Vrije Universiteit (VU), Amsterdam.

The pepper package is split in a number of subpackages:

- :mod:`~pepper.brain` is concerned with managing and querying pepper's triple store database
- :mod:`~pepper.framework` contains the backends and sensory processing needed to run robot apps
- :mod:`~pepper.knowledge` contains pepper's hardwired and internet knowledge
- :mod:`~pepper.language` contains the grammars and scripts to parse and generate natural language
- :mod:`~pepper.responder` contains scripts that reply to certain (natural language) queries

:mod:`~pepper.config` lists all application configuration options
"""

import logging
import enum
import os


# Global Logging Setup
LOGGING_LEVEL = logging.INFO  # INFO for cleaner experiments
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


class ApplicationBackend(enum.Enum):
    SYSTEM = 0
    NAOQI = 1


class ObjectDetectionTarget(enum.Enum):
    AVA = ('localhost', 27001)
    COCO = ('localhost', 27002)
    OID = ('localhost', 27003)


class CameraResolution(enum.Enum):
    NATIVE = -1, -1
    QQQQVGA = 30, 40
    QQQVGA = 60, 80
    QQVGA = 120, 160
    QVGA = 240, 320
    VGA = 480, 640
    VGA4 = 960, 1280


class NAOqiCameraIndex(enum.IntEnum):
    TOP = 0
    BOTTOM = 1
    DEPTH = 2


class NAOqiMicrophoneIndex(enum.IntEnum):
    ALL = 0
    LEFT = 1
    RIGHT = 2
    FRONT = 3
    REAR = 4
