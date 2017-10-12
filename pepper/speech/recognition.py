from google.cloud import speech

class Recognition(object):
    def transcribe(self, audio):
        raise NotImplementedError()


class GoogleRecognition(Recognition):
    def __init__(self, sample_rate = 16000, language_code = 'en-GB'):
        super(GoogleRecognition, self).__init__()

        self._sample_rate = sample_rate
        self._language_code = language_code

        self._config = speech.types.RecognitionConfig(
            encoding = speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz = self.sample_rate,
            language_code = self._language_code
        )

    @property
    def sample_rate(self):
        return self._sample_rate

    @property
    def language_code(self):
        return self.language_code

    @property
    def config(self):
        return self._config

    def transcribe(self, audio):
        response = speech.SpeechClient().recognize(self.config, speech.types.RecognitionAudio(content=audio.tobytes()))
        transcript_confidence = []

        for result in response.results:
            for alternative in result.alternatives:
                transcript_confidence.append([alternative.transcript, alternative.confidence])

        return transcript_confidence


