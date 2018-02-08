import pyaudio
import wave
import numpy as np
from enum import Enum


class Microphone(object):
    def __init__(self, sample_rate, channels, callbacks):
        """
        Microphone Interface

        Parameters
        ----------
        sample_rate: int
            Microphone Sample Rate
        channels: int
            Microphone Channels
        callbacks: list of callable
            Microphone Callbacks
        """
        super(Microphone, self).__init__()

        self._sample_rate = sample_rate
        self._channels = channels
        self._callbacks = callbacks

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
    def callbacks(self):
        """
        Microphone Callback

        Returns
        -------
        callback: list of callable
        """
        return self._callbacks

    @callbacks.setter
    def callbacks(self, value):
        """
        Set Callback

        Parameters
        ----------
        value: list
        """
        self._callbacks = value

    def start(self):
        """Start Microphone Stream"""
        raise NotImplementedError()

    def stop(self):
        """Stop Microphone Stream"""
        raise NotImplementedError()

    def on_audio(self, samples):
        """
        On Audio Callback

        Parameters
        ----------
        samples: np.ndarray
        """

        for callback in self.callbacks:
            callback(samples)


class WaveMicrophone(Microphone):
    def __init__(self, path, callbacks = [], play = False):
        """
        Stream Wave File as if it were Microphone Input

        Parameters
        ----------
        path: str
            Path to Wave File on disk
        callbacks: list of callable
            Microphone Callbacks
        play: bool
            Play file over Speakers or not
        """
        self._wave = wave.open(path, 'rb')
        self._play = play
        super(WaveMicrophone, self).__init__(self._wave.getframerate(), self._wave.getnchannels(), callbacks)

        self._pyaudio = pyaudio.PyAudio()
        self._stream = self._pyaudio.open(self.sample_rate, self.channels,
                                          format=pyaudio.paInt16,
                                          output=True, stream_callback=self._on_audio)

    def start(self):
        """Start Microphone Stream"""
        self._stream.start_stream()

    def stop(self):
        """Stop Microphone Stream"""
        self._stream.stop_stream()
        self._stream.close()

    def _on_audio(self, in_data, frame_count, time_info, status):
        """Pyaudio Callback, ensures realtime"""
        data = self._wave.readframes(frame_count)
        self.on_audio(np.frombuffer(data, np.int16))
        return (data if self._play else np.zeros(frame_count, np.uint16), pyaudio.paContinue)


class SystemMicrophone(Microphone):
    def __init__(self, sample_rate, channels, callbacks = []):
        """
        System Microphone: The microphone of this computer

        Parameters
        ----------
        sample_rate: int
            Microphone Sample Rate
        channels: int
            Microphone Channels
        callbacks: list of callable
            Microphone Callbacks
        """
        super(SystemMicrophone, self).__init__(sample_rate, channels, callbacks)

        self._pyaudio = pyaudio.PyAudio()
        self._stream = self._pyaudio.open(sample_rate, channels, pyaudio.paInt16,
                                          input=True, stream_callback=self._on_audio)

    def start(self):
        """Start Microphone Stream"""
        self._stream.start_stream()

    def stop(self):
        """Stop Microphone Stream"""
        self._stream.stop_stream()
        # self._stream.close()

    def _on_audio(self, in_data, frame_count, time_info, status):
        """Pyaudio Callback, ensures realtime"""
        self.on_audio(np.frombuffer(in_data, np.int16))
        return (None, pyaudio.paContinue)


class PepperMicrophoneMode(Enum):
    # ALL = (48000, 0)
    LEFT = (16000, 1)
    RIGHT = (16000, 2)
    FRONT = (16000, 3)
    REAR = (16000, 4)


class PepperMicrophone(Microphone):
    def __init__(self, session, callbacks = [], mode = PepperMicrophoneMode.FRONT):
        """
        Pepper Microphone

        Parameters
        ----------
        session: qi.Session
            Pepper Session Object (naoqi)
        callbacks: list of callable
            Microphone Callbacks
        mode: PepperMicrophoneMode
            Which Microphone to use
        """
        super(PepperMicrophone, self).__init__(16000, 1, callbacks)

        self._session = session
        self._name = self.__class__.__name__
        self._service = self.session.service("ALAudioDevice")
        self._microphone = self.session.registerService(self._name, self)
        self._service.setClientPreferences(self._name, self.sample_rate, mode.value[1], 0)
        self._service.subscribe(self._name)

        self._listening = False

    @property
    def session(self):
        """
        Returns
        -------
        session: qi.Session
        """
        return self._session

    def start(self):
        """Start Microphone Stream"""
        self._listening = True

    def stop(self):
        """Stop Microphone Stream"""
        self._listening = False

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
        if self._listening:
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