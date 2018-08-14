from pepper.framework import BaseApp, AbstractIntention
from pepper.framework.naoqi import *
from pepper.sensor.asr import GoogleASR
from pepper.sensor.face import OpenFace

from pepper import config

import qi


class NaoqiApp(BaseApp):
    def __init__(self, intention = AbstractIntention()):
        """
        Run Application on Naoqi System (Pepper/Nao)

        Parameters
        ----------
        intention: AbstractIntention
            Intention to start program with
        """
        self._application = qi.Application([self.__class__.__name__, "--qi-url={}".format(config.NAOQI_URL)])
        self._application.start()

        super(NaoqiApp, self).__init__(intention, OpenFace(), GoogleASR(config.LANGUAGE),
            NaoqiCamera(self._application.session, config.CAMERA_RESOLUTION, config.CAMERA_FRAME_RATE),
            NaoqiMicrophone(self._application.session, config.NAOQI_MICROPHONE_INDEX),
            NaoqiTextToSpeech(self._application.session))