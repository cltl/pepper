"""Pepper Configuration File"""

from pepper import ApplicationBackend, CameraResolution, NaoqiMicrophoneIndex, LOGGING_FILE
import json
import os


# Application Settings

# Application Backend to Use (SYSTEM or NAOQI)
# More Backends will be added in the future!
APPLICATION_BACKEND = ApplicationBackend.SYSTEM

# Application Language to use
# Full list of Languages and their formats can be found at
#   https://cloud.google.com/speech-to-text/docs/languages
# Please keep in mind that the internal system is English (en) only
#   Translation happens during Speech-to-Text & Text-to-Speech steps
APPLICATION_LANGUAGE = 'en-GB'


# Application Paths

# pepper/                  PROJECT_ROOT
#   people/                 PEOPLE_ROOT
#       friends/             PEOPLE_FRIENDS_ROOT
#           friend001.bin     files containing OpenFace feature data (nx128, for any n > 0)
#           friend002.bin     the name of each file represents the name of a friend
#           friend003.bin     drag 'n drop people from people/new/ to people/friends to update their status
#           ...
#       new/                 PEOPLE_NEW_ROOT
#           NEW.bin           special file containing OpenFace feature data for all faces in LFW dataset
#           new_person1.bin   files containing OpenFace feature data for each new person met
#           ...
#   pepper/                 PACKAGE_ROOT
#       apps/                application implementations
#       brain/               brain (triple store) interactions
#       framework/           application building blocks
#       knowledge/           knowledge sources
#       language/            natural language processing
#       sensor/              sensory processing
#       ...
#       config.py            << this file >>
#       log.txt              LOG
#       brain_log.trig       BRAIN_LOG_ROOT
#       ...
#   README.md               ReadMe File
#   google_cloud_key.json   Google Cloud Key
#

# Path to Package Root (see tree above)
PACKAGE_ROOT = os.path.dirname(__file__)

# Path to Project Root (see tree above)
PROJECT_ROOT = os.path.join(*os.path.split(PACKAGE_ROOT)[:-1])

# People Root
PEOPLE_ROOT = os.path.join(os.path.dirname(__file__), '../people')

# Root of Robot's "friends"
PEOPLE_FRIENDS_ROOT = os.path.join(PEOPLE_ROOT, 'friends')

# Root of people Robot has "just met"
PEOPLE_NEW_ROOT = os.path.join(PEOPLE_ROOT, 'new')

# Path to GOOGLE_APPLICATION_CREDENTIALS file (.json)
# See for more details: https://cloud.google.com/speech-to-text/docs/quickstart-client-libraries
KEY_GOOGLE_CLOUD = os.path.join(os.path.dirname(__file__), "../google_cloud_key.json")

# Path to other tokens (currently just WolframAlpha)
# See for more details: https://products.wolframalpha.com/spoken-results-api/documentation/
# Please make sure you create this .json file with the following formatting:
# {
#  "wolfram": "<Your Wolfram Alpha Key>"
# }
KEY_WOLFRAM = os.path.join(os.path.dirname(__file__), '../tokens.json')

# General Logging
LOG = LOGGING_FILE

# Brain Logging
BRAIN_LOG_ROOT = os.path.join(PACKAGE_ROOT, "../backups/brain/brain_log_{}")


# Application URLs

# Brain URL (Local GraphDB or Remote Database)
BRAIN_URL_LOCAL = "http://localhost:7200/repositories/leolani"
BRAIN_URL_REMOTE = "http://145.100.58.167:50053/sparql"

# NAOqi Robot URL
NAOQI_IP, NAOQI_PORT = "192.168.1.176", 9559
NAOQI_URL = "tcp://{}:{}".format(NAOQI_IP, NAOQI_PORT)


# Application Sensor Parameters
OBJECT_RECOGNITION_THRESHOLD = 0.5
FACE_RECOGNITION_THRESHOLD = 0.5

MICROPHONE_SAMPLE_RATE = 16000
MICROPHONE_CHANNELS = 1

VOICE_ACTIVITY_DETECTION_THRESHOLD = 0.8

CAMERA_RESOLUTION = CameraResolution.QVGA
CAMERA_FRAME_RATE = 5

# NAOqi Specific Overrides
NAOQI_USE_SYSTEM_CAMERA = False
NAOQI_USE_SYSTEM_MICROPHONE = False
NAOQI_USE_SYSTEM_TEXT_TO_SPEECH = False
NAOQI_MICROPHONE_INDEX = NaoqiMicrophoneIndex.FRONT


# .json file with id tokens, with keys:
#   "wolfram": <appid>
with open(KEY_WOLFRAM) as tokens:
    TOKENS = json.load(tokens)

# Set GOOGLE CREDENTIALS
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_GOOGLE_CLOUD


def get_backend():
    """
    Get Backend based on config.py settings

    Returns
    -------
    backend: AbstractBackend
    """
    backend = None
    if APPLICATION_BACKEND == ApplicationBackend.SYSTEM:
        from pepper.framework.backend.system import SystemBackend
        backend = SystemBackend()
    elif APPLICATION_BACKEND == ApplicationBackend.NAOQI:
        from pepper.framework.backend.naoqi import NaoqiBackend
        backend = NaoqiBackend()
    return backend