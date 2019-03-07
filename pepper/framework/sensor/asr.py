from __future__ import unicode_literals

from pepper import config, logger

from google.cloud import speech, translate_v2
import numpy as np

from typing import List, Iterable


class UtteranceHypothesis(object):
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
        # type: () -> str
        """
        Automatic Speech Recognition Hypothesis Transcript

        Returns
        -------
        transcript: str
        """
        return self._transcript

    @property
    def confidence(self):
        # type: () -> float
        """
        Automatic Speech Recognition Hypothesis Confidence

        Returns
        -------
        confidence: float
        """
        return self._confidence

    def __repr__(self):
        return "<'{}' [{:3.2%}]>".format(self.transcript, self.confidence)


class AbstractTranslator(object):
    def __init__(self, source, target):
        self._source = source.split('-')[0]
        self._target = target.split('-')[0]

    @property
    def source(self):
        return self._source

    @property
    def target(self):
        return self._target

    def translate(self, text):
        raise NotImplementedError()


class GoogleTranslator(AbstractTranslator):
    def __init__(self, source, target):
        super(GoogleTranslator, self).__init__(source, target)

        self._translate = lambda text: text

        if source != target:
            self._translate = lambda text: translate_v2.Client(target_language=self.target).translate(
                text, source_language=self.source, target_language=self.target)['translatedText']

    def translate(self, text):
        return self._translate(text)


class AbstractASR(object):

    MAX_ALTERNATIVES = 10

    def __init__(self, language=config.APPLICATION_LANGUAGE):
        """
        Abstract Automatic Speech Recognition Class

        Parameters
        ----------
        language: str
        """
        self._language = language
        self._log = logger.getChild("{} ({})".format(self.__class__.__name__, self.language))

    @property
    def language(self):
        """
        Automatic Speech Recognition Language

        Returns
        -------
        language: str
        """
        return self._language

    def transcribe(self, audio):
        """
        Transcribe Speech in Audio

        Parameters
        ----------
        audio: numpy.ndarray

        Returns
        -------
        transcript: list of UtteranceHypothesis
        """
        raise NotImplementedError()


class BaseGoogleASR(AbstractASR, GoogleTranslator):
    def __init__(self, language=config.APPLICATION_LANGUAGE, sample_rate=config.MICROPHONE_SAMPLE_RATE, hints=()):
        AbstractASR.__init__(self, language)
        GoogleTranslator.__init__(self, config.APPLICATION_LANGUAGE, config.INTERNAL_LANGUAGE)

        self._client = speech.SpeechClient()
        self._config = speech.types.RecognitionConfig(
            encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16, sample_rate_hertz=sample_rate,
            language_code=language, max_alternatives=self.MAX_ALTERNATIVES,
            speech_contexts=[speech.types.SpeechContext(phrases=hints)])
        self._log = logger.getChild(self.__class__.__name__)
        self._log.debug("Booted ({} -> {})".format(self.source, self.target))


class StreamedGoogleASR(BaseGoogleASR):
    def __init__(self, language=config.APPLICATION_LANGUAGE, sample_rate=config.MICROPHONE_SAMPLE_RATE, hints=()):
        super(StreamedGoogleASR, self).__init__(language, sample_rate, hints)
        self._streaming_config = speech.types.StreamingRecognitionConfig(config=self._config, single_utterance=True)

    def transcribe(self, audio):
        # type: (Iterable[np.ndarray]) -> List[UtteranceHypothesis]
        hypotheses = []
        for response in self._client.streaming_recognize(self._streaming_config, self._request(audio)):
            for result in response.results:
                if result.is_final:
                    for alternative in result.alternatives:
                        hypotheses.append(UtteranceHypothesis(self.translate(alternative.transcript), alternative.confidence))
        return hypotheses

    @staticmethod
    def _request(audio):
        for frame in audio:
            yield speech.types.StreamingRecognizeRequest(audio_content=frame.tobytes())


class SynchronousGoogleASR(BaseGoogleASR):
    def __init__(self, language=config.APPLICATION_LANGUAGE, sample_rate=config.MICROPHONE_SAMPLE_RATE, hints=()):
        super(SynchronousGoogleASR, self).__init__(language, sample_rate, hints)

    def transcribe(self, audio):
        """
        Transcribe Speech in Audio

        Parameters
        ----------
        audio: numpy.ndarray

        Returns
        -------
        hypotheses: List[UtteranceHypothesis]
        """
        hypotheses = []
        for result in self._client.recognize(self._config, self._request(audio)).results:
            for alternative in result.alternatives:
                hypotheses.append(UtteranceHypothesis(self.translate(alternative.transcript), alternative.confidence))
        return hypotheses

    @staticmethod
    def _request(audio):
        return speech.types.RecognitionAudio(content=audio.tobytes())
