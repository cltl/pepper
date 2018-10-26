import enum
import json
import os


class ApplicationTarget(enum.Enum):
    SYSTEM = 0
    NAOQI = 1


class CameraResolution(enum.Enum):
    NATIVE = -1, -1
    QQQQVGA = 30, 40
    QQQVGA = 60, 80
    QQVGA = 120, 160
    QVGA = 240, 320
    VGA = 480, 640
    VGA4 = 960, 1280


class NaoqiCameraIndex(enum.IntEnum):
    TOP = 0
    BOTTOM = 1
    DEPTH = 2


class NaoqiMicrophoneIndex(enum.IntEnum):
    ALL = 0
    LEFT = 1
    RIGHT = 2
    FRONT = 3
    REAR = 4


APPLICATION_TARGET = ApplicationTarget.SYSTEM


def get_backend():
    backend = None
    if APPLICATION_TARGET == ApplicationTarget.SYSTEM:
        from pepper.framework.backend.system import SystemBackend
        backend = SystemBackend()
    elif APPLICATION_TARGET == ApplicationTarget.NAOQI:
        from pepper.framework.backend.naoqi import NaoqiBackend
        backend = NaoqiBackend()
    return backend


PACKAGE_ROOT = os.path.dirname(__file__)
PROJECT_ROOT = os.path.join(*os.path.split(PACKAGE_ROOT)[:-1])

LANGUAGE = 'en-GB'

BRAIN_URL_REMOTE = "http://145.100.58.167:50053/sparql"
BRAIN_URL_LOCAL = "http://localhost:7200/repositories/leolani"
BRAIN_LOG = os.path.join(os.path.dirname(__file__), "brain_log")

MICROPHONE_SAMPLE_RATE = 16000
MICROPHONE_CHANNELS = 1

VAD_VOICE_THRESHOLD = 0.9
VAD_NONVOICE_THRESHOLD = 0.2
VAD_WINDOW_SIZE = 3  # * VAD_FRAME_MS

CAMERA_RESOLUTION = CameraResolution.QVGA
CAMERA_FRAME_RATE = 5

OBJECT_CONFIDENCE_THRESHOLD = 0.5

FACE_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'people', 'friends'))
NEW_FACE_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'people', 'new'))

FACE_RECOGNITION_THRESHOLD = 0.5

NAOQI_IP = "192.168.1.176"
NAOQI_PORT = 9559
NAOQI_URL = "tcp://{}:{}".format(NAOQI_IP, NAOQI_PORT)
NAOQI_MICROPHONE_INDEX = NaoqiMicrophoneIndex.FRONT


# .json file with id tokens, with keys:
#   "wolfram": <appid>
with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tokens.json'))) as tokens:
    TOKENS = json.load(tokens)

# Set GOOGLE CREDENTIALS
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.path.dirname(__file__), "../google_cloud_key.json")