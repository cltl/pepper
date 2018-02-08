import logging

# Logging Module Default Settings, for debugging, switch to level=logging.DEBUG
logging.basicConfig(format='%(asctime)-15s %(levelname)s %(message)s', level=logging.INFO)

# Pepper Address, reference point for all apps (because it will change a lot!)
ADDRESS = '192.168.137.54', 9559


# Import to Package Level
from .app import App

from .speech.microphone import WaveMicrophone, SystemMicrophone, PepperMicrophone
from .vision.camera import PepperCamera, CameraID, CameraColorSpace, CameraResolution

from .speech.recognition import GoogleRecognition
from .speech.utterance import Utterance
