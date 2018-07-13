from pepper.framework.abstract.microphone import AbstractMicrophone
from pepper.framework.enumeration import NaoqiMicrophoneIndex
import numpy as np


class NaoqiMicrophone(AbstractMicrophone):

    SERVICE = "ALAudioDevice"
    RATE = 16000

    def __init__(self, session, index, callbacks = []):
        super(NaoqiMicrophone, self).__init__(
            NaoqiMicrophone.RATE, 4 if index == NaoqiMicrophoneIndex.ALL else 1, callbacks)
        self._service = session.service(NaoqiMicrophone.SERVICE)
        session.registerService(self.__class__.__name__, self)
        self._service.setClientPreferences(self.__class__.__name__, self.rate, int(index), 0)
        self._service.subscribe(self.__class__.__name__)

        self._log.debug("Booted")

    def processRemote(self, channels, samples, timestamp, buffer):
        if self._running:
            audio = np.frombuffer(buffer, np.int16)
            self.on_audio(audio)