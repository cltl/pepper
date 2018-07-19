from pepper.framework import *
import json
import os

LANGUAGE = 'en-GB'

MICROPHONE_SAMPLE_RATE = 16000
MICROPHONE_CHANNELS = 1

VAD_VOICE_THRESHOLD = 0.6
VAD_NONVOICE_THRESHOLD = 0.1

CAMERA_RESOLUTION = CameraResolution.QVGA
CAMERA_FRAME_RATE = 2

OBJECT_CONFIDENCE_THRESHOLD = 0.5

FACE_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'people', 'friends'))
FACE_RECOGNITION_KNOWN_CONFIDENCE_THRESHOLD = 0.9
FACE_RECOGNITION_NEW_DISTANCE_THRESHOLD = 1.0

NAOQI_IP = "192.168.1.176"
NAOQI_PORT = 9559
NAOQI_URL = "tcp://{}:{}".format(NAOQI_IP, NAOQI_PORT)
NAOQI_MICROPHONE_INDEX = NaoqiMicrophoneIndex.FRONT


# .json file with id tokens, with keys:
#   "wolfram": <appid>
with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tokens.json'))) as tokens:
    TOKENS = json.load(tokens)
