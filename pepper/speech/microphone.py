import pyaudio
import numpy as np


class Microphone:
    @property
    def sample_rate(self):
        raise NotImplementedError()

    @property
    def channels(self):
        raise NotImplementedError()

    def get(self, seconds):
        """Get Audio Signal as Numpy Array"""

        raise NotImplementedError()

    def get_spectrum(self, seconds):
        """Get Audio Signal, Frequencies and Power Spectrum as Numpy Arrays"""

        raise NotImplementedError()


class SystemMicrophone(Microphone):

    FORMAT = pyaudio.paInt16
    DATA_TYPE = np.int16
    DATA_TYPE_MAX = np.iinfo(DATA_TYPE).max

    def __init__(self, sample_rate=16000, channels=1):
        self._audio = pyaudio.PyAudio()
        self._stream = self._audio.open(sample_rate, channels, self.FORMAT, True)
        self._sample_rate = sample_rate
        self._channels = channels

    @property
    def sample_rate(self):
        return self._sample_rate

    @property
    def channels(self):
        return self._channels

    def get(self, seconds):
        return np.frombuffer(self._stream.read(int(self.sample_rate * seconds)), self.DATA_TYPE)

    def get_spectrum(self, seconds):
        signal = self.get(seconds)
        spectrum = np.abs(np.fft.rfft(signal)) ** 2 / seconds
        return signal, (spectrum[:len(spectrum) // 2], 4000)

    def __del__(self):
        self._stream.stop_stream()
        self._stream.close()
        self._audio.terminate()