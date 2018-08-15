from pepper.framework import BaseApp, AbstractIntention
from pepper.framework.system import *
from pepper.sensor.asr import GoogleASR
from pepper.sensor.face import OpenFace
from pepper import config


class SystemApp(BaseApp):
    def __init__(self):
        """Run Application on Host System"""
        super(SystemApp, self).__init__(OpenFace(),
                                        GoogleASR(config.LANGUAGE),
                                        SystemCamera(config.CAMERA_RESOLUTION, config.CAMERA_FRAME_RATE),
                                        SystemMicrophone(config.MICROPHONE_SAMPLE_RATE, config.MICROPHONE_CHANNELS),
                                        SystemTextToSpeech())