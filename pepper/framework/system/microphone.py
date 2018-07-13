from pepper.framework.abstract.microphone import AbstractMicrophone

import pyaudio
import numpy as np

import logging


class SystemMicrophone(AbstractMicrophone):
    def __init__(self, rate, channels, callbacks = []):
        super(SystemMicrophone, self).__init__(rate, channels, callbacks)

        self._pyaudio = pyaudio.PyAudio()
        self._microphone = self._pyaudio.open(rate, channels, pyaudio.paInt16, input=True, stream_callback=self._stream)

        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Booted")

    def _stream(self, in_data, frame_count, time_info, status):
        if self._running:
            audio = np.frombuffer(in_data, np.int16)
            self.on_audio(audio)
            return (None, pyaudio.paContinue)