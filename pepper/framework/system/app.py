from pepper.framework.abstract import BaseApp, AbstractIntention
from pepper.framework.system import *
from pepper.framework.asr import GoogleASR
from pepper.framework.face import OpenFace
from pepper import config


class SystemApp(BaseApp):
    def __init__(self, intention = AbstractIntention()):
        """
        Run Application on Host System

        Parameters
        ----------
        intention: AbstractIntention
            Intention to start program with
        """
        super(SystemApp, self).__init__(intention,
                                        SystemCamera(config.CAMERA_RESOLUTION, config.CAMERA_FRAME_RATE),
                                        OpenFace(),
                                        SystemMicrophone(config.MICROPHONE_SAMPLE_RATE, config.MICROPHONE_CHANNELS),
                                        GoogleASR(config.LANGUAGE),
                                        SystemTextToSpeech())