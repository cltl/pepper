import pyaudio
import numpy as np
from enum import Enum

class Microphone(object):

    def __init__(self, sample_rate, channels, callback):
        """
        Microphone Interface

        Parameters
        ----------
        sample_rate: int
            Microphone Sample Rate
        channels: int
            Microphone Channels
        callback: callable
            Microphone Callback
        """
        super(Microphone, self).__init__()

        self._sample_rate = sample_rate
        self._channels = channels
        self._callback = callback

    @property
    def sample_rate(self):
        """
        Microphone Sample Rate

        Returns
        -------
        sample_rate: int
        """
        return self._sample_rate

    @property
    def channels(self):
        """
        Microphone Channels

        Returns
        -------
        channels: int
        """
        return self._channels

    @property
    def callback(self):
        """
        Microphone Callback

        Returns
        -------
        callback: callable
        """
        return self._callback

    def start(self):
        """Start Microphone Stream"""
        raise NotImplementedError()

    def stop(self):
        """Stop Microphone Stream"""
        raise NotImplementedError()

    def on_audio(self, samples):
        self.callback(samples)


class SystemMicrophone(Microphone):
    def __init__(self, sample_rate, channels, callback):
        super(SystemMicrophone, self).__init__(sample_rate, channels, callback)

        self._microphone = pyaudio.PyAudio()
        self._stream = self._microphone.open(sample_rate, channels, pyaudio.paInt16, True,
                                             stream_callback=self._on_audio)

    def start(self):
        self._stream.start_stream()

    def stop(self):
        self._stream.stop_stream()
        self._stream.close()

    def _on_audio(self, in_data, frame_count, time_info, status):
        self.on_audio(np.frombuffer(in_data, np.int16))
        return (None, pyaudio.paContinue)


class PepperMicrophoneMode(Enum):
    ALL = (48000, 0)
    LEFT = (16000, 1)
    RIGHT = (16000, 2)
    FRONT = (16000, 3)
    REAR = (16000, 4)


class PepperMicrophone(Microphone):
    def __init__(self, session, callback, mode = PepperMicrophoneMode.FRONT):
        super(PepperMicrophone, self).__init__(mode.value[0], mode.value[0] // 16000, callback)

        self._session = session
        self._name = self.__class__.__name__
        self._service = self.session.service("ALAudioDevice")
        self._microphone = self.session.registerService(self._name, self)
        self._service.setClientPreferences(self._name, self.sample_rate, self.channels, 0)
        self._service.subscribe(self._name)

    @property
    def session(self):
        return self._session

    def process(self, channels, samples, timestamp, buffer):
        """
        Process Raw Microphone Signal on Local Event (On Pepper)

        Parameters
        ----------
        channels: int
            Number of Channels
        samples: int
            Sample Rate in Hertz
        timestamp: list of int
            Number of seconds and microseconds since device boot
        buffer: bytes
            Raw Microphone Data
        """
        self.on_audio(np.frombuffer(buffer, np.int16))

    def processRemote(self, channels, samples, timestamp, buffer):
        """
        Process Raw Microphone Signal on Remote Event (On Remote Machine)

        Parameters
        ----------
        channels: int
            Number of Channels
        samples: int
            Sample Rate in Hertz
        timestamp: list of int
            Number of seconds and microseconds since device boot
        buffer: bytes
            Raw Microphone Data
        """
        self.process(channels, samples, timestamp, buffer)



if __name__ == "__main__":
    from time import sleep

    def on_audio(data):
        print(len(data))

    mic = SystemMicrophone(16000, 1, on_audio)

    mic.start()
    sleep(5)
    mic.stop()