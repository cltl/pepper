from google.cloud import speech as google_speech

import numpy as np

from time import time
from threading import Thread


class Recognition(Thread):

    FREQUENCY_RANGE = (85, 255)
    THRESHOLD = 1E10
    MIN_LENGTH = 0.3
    INTERVAL = 0.2
    WINDOW = 0.1
    BUFFER = 3

    def __init__(self, microphone):
        super(Recognition, self).__init__()
        self._microphone = microphone
        self._stop = False

    @property
    def microphone(self):
        return self._microphone

    def stop(self):
        self._stop = True

    def run(self):
        self._stop = False

        buffer = []
        recording = False
        silence_start = 0.0
        recording_start = 0.0

        while not self._stop:
            signal, (spectrum, frequency) = self.microphone.get_spectrum(self.WINDOW)

            has_speech = self._has_speech(spectrum, frequency)

            if recording:
                buffer.append(signal)

                if not has_speech:
                    if silence_start:
                        if time() - silence_start > self.INTERVAL:
                            if time() - recording_start > self.MIN_LENGTH:
                                self.on_speech(np.concatenate(buffer))

                            recording = False
                            silence_start = 0.0
                            recording_start = 0.0

                    else:  # if not silence_start
                        silence_start = time()
                else:  # if has_speech
                    silence_start = 0.0

            elif has_speech:  # not recording but has_speech
                recording = True
                recording_start = time()
                buffer.append(signal)

            else:  # not recording and no speech
                buffer.append(signal)
                while len(buffer) > self.BUFFER:
                    buffer.pop(0)

    def on_speech(self, signal):
        raise NotImplementedError()

    def _has_speech(self, spectrum, frequency):
        lower_bound = int(self.FREQUENCY_RANGE[0] / (float(frequency) / len(spectrum)))
        upper_bound = int(self.FREQUENCY_RANGE[1] / (float(frequency) / len(spectrum)))

        spectrum_range = spectrum[lower_bound:upper_bound]

        return np.mean(spectrum_range) > self.THRESHOLD


class GoogleRecognition(Recognition):
    def __init__(self, microphone, on_transcribe, language_code='en-GB'):
        super(GoogleRecognition, self).__init__(microphone)

        self._language_code = language_code
        self.on_transcribe = on_transcribe

        self._config = google_speech.types.RecognitionConfig(
            encoding = google_speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz = microphone.sample_rate,
            language_code = language_code
        )

    @property
    def language_code(self):
        return self._language_code

    @property
    def config(self):
        return self._config

    def on_speech(self, signal):
        audio = google_speech.types.RecognitionAudio(content = signal.tobytes())
        client = google_speech.SpeechClient()
        response = client.recognize(self.config, audio)

        for result in response.results:
            for alternative in result.alternatives:
                self.on_transcribe(alternative.transcript, alternative.confidence)