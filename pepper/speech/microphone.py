import pyaudio
import numpy as np
from enum import Enum
from time import sleep


class Microphone(object):
    """Abstract Microphone Class"""

    @property
    def rate(self):
        """Get microphone sample rate in hertz"""
        raise NotImplementedError()

    @property
    def channels(self):
        """Get number of microphone channels"""
        raise NotImplementedError()

    def get(self, seconds):
        """Get Audio Signal as Numpy Array"""
        raise NotImplementedError()


class PepperMicrophoneMode(Enum):
    ALL = (48000, 0)
    LEFT = (16000, 1)
    RIGHT = (16000, 2)
    FRONT = (16000, 3)
    REAR = (16000, 4)


class PepperMicrophoneProcessor(object):
    def __init__(self):
        """Process Microphone Events and Buffer Signal"""

        self._buffer = []
        self._listen = False

    def get(self, seconds):
        """
        Get Audio Signal as Numpy Array

        Parameters
        ----------
        seconds: number of seconds to sample

        Returns
        -------
        signal: np.ndarray
        """

        self._listen = True
        sleep(seconds)
        self._listen = False

        result = np.concatenate(self._buffer)
        self._buffer = []

        return result

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
        if self._listen:
            data = np.frombuffer(buffer, np.int16).reshape(samples)
            self._buffer.append(data)

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


class PepperMicrophone(Microphone):

    def __init__(self, session, mode = PepperMicrophoneMode.FRONT):
        """
        Use Pepper's Microphone

        Parameters
        ----------
        session: qi.Session
            Session to subscribe microphone to
        mode: PepperMicrophoneMode
            Sampling Mode (sampling rate & microphone location)
        """
        self._session = session
        self._service = self.session.service("ALAudioDevice")
        self._processor = PepperMicrophoneProcessor()
        self._microphone = self.session.registerService(self.name, self._processor)

        self._sample_rate = mode.value[0]
        self._channels = 1 if mode.value[1] else 4

        self.service.setClientPreferences(self.name, self.rate, self.channels, 0)
        self.service.subscribe(self.name)

    @property
    def name(self):
        """
        Returns
        -------
        name: str
            Name of Class
        """
        return self.__class__.__name__

    @property
    def session(self):
        """
        Returns
        -------
        session: qi.Session
            Session to subscribe microphone to
        """
        return self._session

    @property
    def service(self):
        """
        Returns
        -------
        service
            The ALAudioDevice service
        """
        return self._service

    @property
    def rate(self):
        """
        Returns
        -------
        sample_rate: int
            Sample rate in Hertz
        """
        return self._sample_rate

    @property
    def channels(self):
        """
        Returns
        -------
        channels: int
            Number of channels
        """
        return self._channels

    def get(self, seconds):
        """
        Get Audio Signal as Numpy Array

        Parameters
        ----------
        seconds: number of seconds to sample

        Returns
        -------
        signal: np.ndarray
        """
        return self._processor.get(seconds)


class SystemMicrophone(Microphone):

    FORMAT = pyaudio.paInt16
    DATA_TYPE = np.int16
    DATA_TYPE_MAX = np.iinfo(DATA_TYPE).max

    def __init__(self, sample_rate=16000, channels=1):
        """
        Use Local System Microphone

        Parameters
        ----------
        sample_rate: int
            Sample rate in Hertz
        channels: int
            Number of channels
        """
        self._audio = pyaudio.PyAudio()
        self._stream = self._audio.open(sample_rate, channels, self.FORMAT, True)
        self._sample_rate = sample_rate
        self._channels = channels

    @property
    def rate(self):
        """
        Returns
        -------
        sample_rate: int
            Sample rate in Hertz
        """
        return self._sample_rate

    @property
    def channels(self):
        """
        Returns
        -------
        channels: int
            Number of channels
        """
        return self._channels

    def get(self, seconds):
        """
        Get Audio Signal as Numpy Array

        Parameters
        ----------
        seconds: number of seconds to sample

        Returns
        -------
        signal: np.ndarray
        """
        return np.frombuffer(self._stream.read(int(self.rate * seconds)), self.DATA_TYPE)

    def __del__(self):
        self._stream.stop_stream()
        self._stream.close()
        self._audio.terminate()