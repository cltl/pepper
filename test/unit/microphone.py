from pepper.framework import AbstractMicrophone
from pepper import config


import numpy as np

from collections import deque
from time import time, sleep



class MicrophoneTest(object):

    DT_BUFFER_LENGTH = 100

    def __init__(self):
        self._t0 = time()
        self._dt_buffer = deque(maxlen=MicrophoneTest.DT_BUFFER_LENGTH)

    @property
    def microphone(self):
        """
        Returns
        -------
        microphone: AbstractMicrophone
        """
        raise NotImplementedError()

    def on_audio(self, audio):
        t1 = time()
        dt = t1 - self._t0
        self._dt_buffer.append(dt)
        self._t0 = t1

        kBs = (audio.nbytes / 1024.0) / float(dt)
        kBs_average = float(audio.nbytes / 1024.0) / np.mean(self._dt_buffer)

        print "\rMicrophone Stream: {:3.2f} kB/s ~ {:3.2f} kB/s (average)".format(kBs, kBs_average),

    def run(self):
        self.microphone.start()

        print("{} @ {} Hz : {} channel(s) -> {:3.2f} kB/s expected".format(
            self.microphone.__class__.__name__,
            self.microphone.rate,
            self.microphone.channels,
            self.microphone.rate * 2.0 / 1024.0))

        while True:
            sleep(0.1)


class SystemMicrophoneTest(MicrophoneTest):
    def __init__(self):
        super(SystemMicrophoneTest, self).__init__()

        from pepper.framework.system import SystemMicrophone
        self._microphone = SystemMicrophone(config.MICROPHONE_SAMPLE_RATE, config.MICROPHONE_CHANNELS, [self.on_audio])

        self.run()

    @property
    def microphone(self):
        return self._microphone


class NaoqiMicrophoneTest(MicrophoneTest):
    def __init__(self):
        super(NaoqiMicrophoneTest, self).__init__()

        from pepper.framework.naoqi import NaoqiApp, NaoqiMicrophone
        self._session = NaoqiApp.create_session()
        self._microphone = NaoqiMicrophone(self._session, config.NAOQI_MICROPHONE_INDEX, [self.on_audio])

        self.run()

    @property
    def microphone(self):
        return self._microphone


if __name__ == '__main__':
    SystemMicrophoneTest()
