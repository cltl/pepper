from pepper.framework.abstract.microphone import AbstractMicrophone

import pyaudio
import numpy as np

from typing import List, Callable


class SystemMicrophone(AbstractMicrophone):
    """
    System Microphone

    Parameters
    ----------
    rate: int
        Samples per Second
    channels: int
        Number of Channels
    callbacks: list of callable
        Functions to call each time some audio samples are captured
    """

    def __init__(self, rate, channels, callbacks=[]):
        # type: (int, int, List[Callable[[np.ndarray], None]]) -> None
        super(SystemMicrophone, self).__init__(rate, channels, callbacks)

        # Open Microphone Stream
        self._pyaudio = pyaudio.PyAudio()
        self._microphone = self._pyaudio.open(rate, channels, pyaudio.paInt16, input=True, stream_callback=self._stream)

        self._log.debug("Booted")

    def _stream(self, in_data, frame_count, time_info, status):
        """
        System Microphone Audio Stream Handler

        Parameters
        ----------
        in_data: bytes
        """
        audio = np.frombuffer(in_data, np.int16)
        self.on_audio(audio)
        return None, pyaudio.paContinue
