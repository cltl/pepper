from pepper.speech.microphone import WaveFileMicrophone, SystemMicrophone

from webrtcvad import Vad
import numpy as np

from threading import Thread
import itertools


class Utterance(object):

    FRAME_LENGTH_MS = 30

    MICROPHONE_LENGTH_MS = FRAME_LENGTH_MS * 10
    BUFFER_LENGTH_MS = FRAME_LENGTH_MS * 30

    MICROPHONE_SIZE = MICROPHONE_LENGTH_MS / FRAME_LENGTH_MS
    BUFFER_SIZE = BUFFER_LENGTH_MS / FRAME_LENGTH_MS

    SPEECH_THRESHOLD = 0.9
    NON_SPEECH_THRESHOLD = 0.7

    def __init__(self, microphone, callback, mode=3):
        self._microphone = microphone
        self._sample_rate = microphone.sample_rate
        self._callback = callback
        self._vad = Vad(mode)

        self._is_running = False
        self._thread = None

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
        self._is_running = True
        self._thread = Thread(target=self.run)
        self._thread.start()

    def stop(self):
        self._is_running = False
        if self._thread:
            self._thread.join()

    def run(self):
        frame_bytes = 2 * (self.FRAME_LENGTH_MS * self.sample_rate) // 1000
        frame_length = frame_bytes // 2

        audio_ringbuffer = np.zeros((self.BUFFER_SIZE, frame_length), np.int16)
        speech_ringbuffer = np.zeros(self.BUFFER_SIZE, np.bool)

        speech = False
        speech_audio_buffer = []

        buffer_index = 0

        while self._is_running:
            audio = self.microphone.get(self.MICROPHONE_LENGTH_MS * 1E-3)

            for frame_index in range(self.MICROPHONE_SIZE):
                frame = audio[frame_index * frame_length:(frame_index+1)*frame_length]

                audio_ringbuffer[buffer_index] = frame
                speech_ringbuffer[buffer_index] = self.vad.is_speech(frame.tobytes(), self.sample_rate, frame_length)

                buffer_index = (buffer_index + 1) % self.BUFFER_SIZE

                if speech:
                    if np.mean(speech_ringbuffer) < self.NON_SPEECH_THRESHOLD:
                        speech = False

                        self.on_utterance(np.concatenate(speech_audio_buffer))
                        speech_audio_buffer = []

                    else:
                        speech_audio_buffer.append(frame)

                else:
                    if np.mean(speech_ringbuffer) > self.SPEECH_THRESHOLD:
                        speech = True

                        # Append some Silence to audio
                        speech_audio_buffer.append(np.zeros(frame_length, np.int16))

                        # Append current contents of audio ringbuffer to speech audio output
                        for index in itertools.chain(range(buffer_index, self.BUFFER_SIZE), range(0, buffer_index)):
                            speech_audio_buffer.append(audio_ringbuffer[index].flatten())

    def on_utterance(self, audio):
        self._callback(audio)


if __name__ == "__main__":
    from pepper.speech.recognition import GoogleRecognition

    def on_utterance(audio):
        print("{0}".format(GoogleRecognition().transcribe(audio)[0][0]))


    mic = WaveFileMicrophone(16000, r"C:\Users\Bram\Documents\Pepper\data\speech\noisy_speech_2\10db.wav")
    # microphone = SystemMicrophone()
    utterance = Utterance(mic, on_utterance)
    utterance.start()
