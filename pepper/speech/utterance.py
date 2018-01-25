from microphone import Microphone
from webrtcvad import Vad
import numpy as np

from threading import Thread


class Utterance(object):

    FRAME_MS = 10  # Must be either 10/20/30 ms, according to webrtcvad specification
    WINDOW_SIZE = 30  # Sliding Window Length (Multiples of Frame MS)

    VOICE_THRESHOLD = 0.7
    NONVOICE_THRESHOLD = 0.2

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
        self._audio_ringbuffer = np.zeros((self.WINDOW_SIZE, self._frame_size), np.int16)
        self._vad_ringbuffer = np.zeros(self.WINDOW_SIZE, np.bool)

        self._empty_space = np.random.uniform(-10, 10, self.sample_rate//2).astype(np.int16).tobytes()

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

    def process_frame(self, frame):
        self._audio_ringbuffer[self._ringbuffer_index] = frame
        self._vad_ringbuffer[self._ringbuffer_index] = self.vad.is_speech(frame.tobytes(), self.sample_rate, len(frame))
        self._ringbuffer_index = (self._ringbuffer_index + 1) % self.WINDOW_SIZE

    def process_voice(self, frame):
        activation = np.mean(self._vad_ringbuffer)

        if self._voice:
            if activation > self.NONVOICE_THRESHOLD:
                self._voice_buffer.extend(frame.tobytes())  # Add Frame to Voice Buffer
            else:
                self._voice = False  # Stop Recording Voice

                # Call Utterance Callback (in Thread, to prevent blocking)
                self._voice_buffer.extend(self._empty_space)
                Thread(target=self.on_utterance, args=(np.frombuffer(self._voice_buffer, np.int16),)).start()

                self._voice_buffer = bytearray()  # Clear Voice Buffer
        else:
            if activation > self.VOICE_THRESHOLD:
                self._voice = True  # Start Recording Voice

                # Add Buffered Audio to Voice Buffer
                self._voice_buffer.extend(self._empty_space)
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

