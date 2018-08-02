from enum import Enum, IntEnum


class CameraResolution(Enum):
    QQQQVGA = 30, 40
    QQQVGA = 60, 80
    QQVGA = 120, 160
    QVGA = 240, 320
    VGA = 480, 640
    VGA4 = 960, 1280


class NaoqiCameraIndex(IntEnum):
    TOP = 0
    BOTTOM = 1
    DEPTH = 2


class NaoqiMicrophoneIndex(IntEnum):
    ALL = 0
    LEFT = 1
    RIGHT = 2
    FRONT = 3
    REAR = 4


from .abstract import *
