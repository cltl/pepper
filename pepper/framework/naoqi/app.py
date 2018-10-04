from pepper.framework import BaseApp, AbstractIntention
from pepper.framework.naoqi import *
from pepper.sensor.asr import GoogleASR
from pepper.sensor.face import OpenFace

from pepper import config

import qi


class NaoqiApp(BaseApp):
    def __init__(self):
        """Run Application on Naoqi System (Pepper/Nao)"""
        self._session = NaoqiApp.create_session()

        super(NaoqiApp, self).__init__(OpenFace(), GoogleASR(config.LANGUAGE),
            NaoqiCamera(self._session, config.CAMERA_RESOLUTION, config.CAMERA_FRAME_RATE),
            NaoqiMicrophone(self._session, config.NAOQI_MICROPHONE_INDEX),
            NaoqiTextToSpeech(self._session))

    @staticmethod
    def create_session():
        application = qi.Application([NaoqiApp.__name__, "--qi-url={}".format(config.NAOQI_URL)])
        try: application.run()
        except RuntimeError as e:
            raise RuntimeError("Couldn't connect to robot, check if robot IP is set correctly in pepper/config.py"
                               "\n\tOriginal Error: {}".format(e))
        return application.session