from microphone import Microphone
from webrtcvad import Vad
import numpy as np

from threading import Thread


class Utterance(object):

    FRAME_MS = 10  # Must be either 10/20/30 ms, according to webrtcvad specification
    BUFFER_SIZE = 100 # Buffer Size
    WINDOW_SIZE = 30  # Sliding Window Length (Multiples of Frame MS)

    VOICE_THRESHOLD = 0.9
    NONVOICE_THRESHOLD = 0

    def __init__(self, microphone, callback, mode=3):
        """

        Parameters
        ----------
        microphone: Microphone
            Microphone to extract Utterances from
        callback: callable
            On Utterance Callback
        mode: int
            Voice Activity Detection (VAD) 'Aggressiveness' (1..3)
        """
        self._microphone = microphone
        self._microphone.callbacks += [self.on_audio]
        self._sample_rate = microphone.sample_rate

        self._callback = callback
        self._vad = Vad(mode)

        self._frame_size = self.FRAME_MS * self.sample_rate // 1000

        self._ringbuffer_index = 0
        self._audio_ringbuffer = np.zeros((self.BUFFER_SIZE, self._frame_size), np.int16)
        self._vad_ringbuffer = np.zeros(self.BUFFER_SIZE, np.bool)

        self._audio_buffer = bytearray()
        self._voice_buffer = bytearray()

        self._voice = False

    @property
    def microphone(self):
        return self._microphone

    @property
    def sample_rate(self):
        return self._sample_rate

    @property
    def callback(self):
        return self._callback

    @property
    def vad(self):
        return self._vad

    def start(self):
        self.microphone.start()

    def stop(self):
        self.microphone.stop()

    def activation(self):
        window = np.arange(self._ringbuffer_index - self.WINDOW_SIZE, self._ringbuffer_index) % self.BUFFER_SIZE
        return np.mean(self._vad_ringbuffer[window])

    def process_frame(self, frame):
        self._audio_ringbuffer[self._ringbuffer_index] = frame
        self._vad_ringbuffer[self._ringbuffer_index] = self.vad.is_speech(frame.tobytes(), self.sample_rate, len(frame))
        self._ringbuffer_index = (self._ringbuffer_index + 1) % self.BUFFER_SIZE

    def process_voice(self, frame):

        activation = self.activation()

        if self._voice:
            if activation > self.NONVOICE_THRESHOLD:
                self._voice_buffer.extend(frame.tobytes())  # Add Frame to Voice Buffer
            else:
                self._voice = False  # Stop Recording Voice

                for i in range(self.WINDOW_SIZE//2):
                    self._voice_buffer.extend(frame.tobytes())

                result = np.frombuffer(self._voice_buffer, np.int16)

                # Call Utterance Callback (in Thread, to prevent blocking)
                Thread(target=self.on_utterance, args=(result,)).start()
                # self.on_utterance(result)

                self._voice_buffer = bytearray()  # Clear Voice Buffer
        else:
            if activation > self.VOICE_THRESHOLD:
                self._voice = True  # Start Recording Voice

                # Add Buffered Audio to Voice Buffer
                self._voice_buffer.extend(self._audio_ringbuffer[self._ringbuffer_index:].tobytes())
                self._voice_buffer.extend(self._audio_ringbuffer[:self._ringbuffer_index].tobytes())

    def on_audio(self, audio):
        self._audio_buffer.extend(audio.tobytes())

        while len(self._audio_buffer) > 2 * self._frame_size:
            frame = np.frombuffer(self._audio_buffer[:2*self._frame_size], np.int16)
            self.process_frame(frame)
            self.process_voice(frame)
            del self._audio_buffer[:2*self._frame_size]

    def on_utterance(self, audio):
        self._callback(audio)


if __name__ == "__main__":
    from microphone import WaveMicrophone
    from pepper.speech.recognition import GoogleRecognition
    from time import sleep

    def on_utterance(audio):
        print(GoogleRecognition().transcribe(audio))

    mic = WaveMicrophone(r"C:\Users\Bram\Documents\Pepper\data\speech\noisy_speech_2\10db.wav", play=True)
    utterance = Utterance(mic, on_utterance)
    utterance.start()
    sleep(50)
    utterance.stop()

