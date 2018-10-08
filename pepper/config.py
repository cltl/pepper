from pepper.framework import *

import enum
import json
import os


class ApplicationTarget(enum.Enum):
    SYSTEM = 0
    NAOQI = 1

APPLICATION_TARGET = ApplicationTarget.SYSTEM

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

CAMERA_RESOLUTION = CameraResolution.QVGA
CAMERA_FRAME_RATE = 2

OBJECT_CONFIDENCE_THRESHOLD = 0.5

FACE_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'people', 'friends'))
NEW_FACE_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'people', 'new'))

FACE_RECOGNITION_THRESHOLD = 0.9
FACE_RECOGNITION_NEW_DISTANCE_THRESHOLD = 1.2

NAOQI_IP = "192.168.1.176"
NAOQI_PORT = 9559
NAOQI_URL = "tcp://{}:{}".format(NAOQI_IP, NAOQI_PORT)
NAOQI_MICROPHONE_INDEX = NaoqiMicrophoneIndex.FRONT

# Add-ons
REALTIME_STATISTICS = True
SHOW_VIDEO_FEED = False
SAVE_VIDEO_FEED = False


# .json file with id tokens, with keys:
#   "wolfram": <appid>
with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tokens.json'))) as tokens:
    TOKENS = json.load(tokens)