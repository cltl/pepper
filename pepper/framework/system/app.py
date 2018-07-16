from pepper.framework.abstract import AbstractApp
from pepper.framework.system import *
from pepper.framework.asr import GoogleASR
from pepper.framework.face import OpenFace
from pepper import config


class SystemApp(AbstractApp):
    def __init__(self):
        super(SystemApp, self).__init__(SystemCamera(config.CAMERA_RESOLUTION, config.CAMERA_FRAME_RATE), OpenFace(),
                                        SystemMicrophone(config.MICROPHONE_SAMPLE_RATE, config.MICROPHONE_CHANNELS),
                                        GoogleASR(config.LANGUAGE), SystemTextToSpeech())