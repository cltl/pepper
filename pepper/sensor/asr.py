from __future__ import unicode_literals

from pepper import config, logger

from google.cloud import speech, translate_v2


class ASRHypothesis(object):
    def __init__(self, transcript, confidence):
        """
        Automatic Speech Recognition Hypothesis

        Parameters
        ----------
        transcript: str
        confidence: float
        """
        self._transcript = transcript
        self._confidence = confidence

    @property
    def transcript(self):
        return self._transcript

    @property
    def confidence(self):
        return self._confidence

    def __repr__(self):
        return "<'{}' [{:3.2%}]>".format(self.transcript, self.confidence)


class AbstractASR(object):

    MAX_ALTERNATIVES = 1

    def __init__(self, language='en-GB'):
        """
        Abstract Automatic Speech Recognition Class

        Parameters
        ----------
        language: str
        """
        self._language = language

        self._translate_client = None
        self._source_language = language[:2]

        if self._source_language != 'en':
            self._translate_client = translate_v2.Client()

        self._log = logger.getChild("{} ({})".format(self.__class__.__name__, self.language))

    @property
    def language(self):
        return self._language

    def translate(self, transcript):
        if self._translate_client is not None:
            return self._translate_client.translate(transcript, source_language=self._source_language)['translatedText']
        else:
            return transcript

    def transcribe(self, audio):
        """
        Transcribe Speech in Audio

        Parameters
        ----------
        audio: numpy.ndarray

        Returns
        -------
        transcript: list of ASRHypothesis
        """
        raise NotImplementedError()


class BaseGoogleASR(AbstractASR):
    def __init__(self, language=config.APPLICATION_LANGUAGE, sample_rate=config.MICROPHONE_SAMPLE_RATE, hints=()):
        super(BaseGoogleASR, self).__init__(language)

        self._client = speech.SpeechClient()
        self._config = speech.types.RecognitionConfig(
            encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=sample_rate,
            language_code=language,
            max_alternatives=self.MAX_ALTERNATIVES,
            speech_contexts=[speech.types.SpeechContext(phrases=hints)])
        self._log = logger.getChild(self.__class__.__name__)


class StreamedGoogleASR(BaseGoogleASR):
    def __init__(self, language=config.APPLICATION_LANGUAGE, sample_rate=config.MICROPHONE_SAMPLE_RATE, hints=()):
        super(StreamedGoogleASR, self).__init__(language, sample_rate, hints)
        self._streaming_config = speech.types.StreamingRecognitionConfig(config=self._config)
        self._log.debug("Booted")

    def transcribe(self, audio):
        hypotheses = []
        for response in self._client.streaming_recognize(self._streaming_config, self._request(audio)):
            for result in response.results:
                if result.is_final:
                    for alternative in result.alternatives:
                        hypotheses.append(ASRHypothesis(self.translate(alternative.transcript), alternative.confidence))
        return hypotheses

    @staticmethod
    def _request(audio):
        for frame in audio:
            yield speech.types.StreamingRecognizeRequest(audio_content=frame.tobytes())


class SynchronousGoogleASR(BaseGoogleASR):
    def __init__(self, language=config.APPLICATION_LANGUAGE, sample_rate=config.MICROPHONE_SAMPLE_RATE, hints=()):
        super(SynchronousGoogleASR, self).__init__(language, sample_rate, hints)
        self._log.debug("Booted")

    def transcribe(self, audio):
        """
        Transcribe Speech in Audio

        Parameters
        ----------
        audio: numpy.ndarray

        Returns
        -------
        hypotheses: List[ASRHypothesis]
        """
        hypotheses = []
        for result in self._client.recognize(self._config, self._request(audio)).results:
            for alternative in result.alternatives:
                hypotheses.append(ASRHypothesis(self.translate(alternative.transcript), alternative.confidence))
        return hypotheses

    @staticmethod
    def _request(audio):
        return speech.types.RecognitionAudio(content=audio.tobytes())
