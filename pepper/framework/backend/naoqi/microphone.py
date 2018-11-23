from pepper.framework.abstract.microphone import AbstractMicrophone
from pepper.config import NaoqiMicrophoneIndex
import numpy as np


class NAOqiMicrophone(AbstractMicrophone):

    SERVICE = "ALAudioDevice"
    RATE = 16000

    def __init__(self, session, index, callbacks = []):
        """
        NAOqi Microphone

        Parameters
        ----------
        session: qi.Session
            Qi Application Session
        index: NaoqiMicrophoneIndex or int
            Which Microphone to Use
        callbacks: list of callable
            On Audio Callbacks
        """
        super(NAOqiMicrophone, self).__init__(
            NAOqiMicrophone.RATE, 4 if index == NaoqiMicrophoneIndex.ALL else 1, callbacks)

        # Register Service and Subscribe this class as callback
        self._service = session.service(NAOqiMicrophone.SERVICE)
        session.registerService(self.__class__.__name__, self)
        self._service.setClientPreferences(self.__class__.__name__, self.rate, int(index), 0)
        self._service.subscribe(self.__class__.__name__)

        self._log.debug("Booted")

    def processRemote(self, channels, samples, timestamp, buffer):
        """
        Process Audio Window from Pepper/Nao

        This function must be called "processRemote", according to Naoqi specifications.

        Parameters
        ----------
        channels: int
            Number of Channels
        samples: int
            Number of Samples
        timestamp: (int, int)
            seconds, millis since boot
        buffer: bytes
            Audio Buffer
        """
        audio = np.frombuffer(buffer, np.int16)
        self.on_audio(audio)