from pepper.framework.abstract import AbstractBackend
from pepper.framework.backend.system import SystemCamera, SystemMicrophone, SystemTextToSpeech
from pepper.framework.backend.naoqi import NaoqiCamera, NaoqiMicrophone, NaoqiTextToSpeech
from pepper import config

import qi


class NaoqiBackend(AbstractBackend):
    def __init__(self, url=config.NAOQI_URL, camera_resolution=config.CAMERA_RESOLUTION,
                 camera_rate=config.CAMERA_FRAME_RATE, microphone_index=config.NAOQI_MICROPHONE_INDEX,
                 language=config.APPLICATION_LANGUAGE, system_camera=False, system_microphone=False, system_text_to_speech=False):
        """
        Initialize Naoqi Backend

        Parameters
        ----------
        url: str
        camera_resolution: pepper.framework.abstract.camera.CameraResolution
        camera_rate: int
        microphone_index: int
        language: str
        """
        self._url = url
        self._session = self.create_session(self._url)

        super(NaoqiBackend, self).__init__(
            SystemCamera(camera_resolution, camera_rate) if system_camera else NaoqiCamera(self.session, camera_resolution, camera_rate),
            SystemMicrophone(16000, 1) if system_microphone else NaoqiMicrophone(self.session, microphone_index),
            SystemTextToSpeech(language) if system_text_to_speech else NaoqiTextToSpeech(self.session, language))

    @property
    def url(self):
        """
        Returns
        -------
        url: str
        """
        return self._url

    @property
    def session(self):
        """
        Returns
        -------
        session: qi.Session
        """
        return self._session

    @staticmethod
    def create_session(url):
        """
        Create Qi Session with Pepper/Nao Robot

        Parameters
        ----------
        url: str

        Returns
        -------
        session: qi.Session
        """
        application = qi.Application([NaoqiBackend.__name__, "--qi-url={}".format(url)])
        try: application.start()
        except RuntimeError as e:
            raise RuntimeError("Couldn't connect to robot @ {}\n\tOriginal Error: {}".format(url, e))
        return application.session