from __future__ import unicode_literals

from google.cloud import speech
import logging


class AbstractASR(object):
    """Abstract Speech Recognition Class"""

    def transcribe(self, audio):
        """
        Transcribe Speech in Audio

        Parameters
        ----------
        audio: numpy.ndarray

        Returns
        -------
        transcript: list of (str, float)
            List of (<transcript>, <confidence>) pairs, one for each hypothesis
        """
        raise NotImplementedError()


class GoogleASR(AbstractASR):
    def __init__(self, language='en-GB', sample_rate=16000, max_alternatives=20):
        """
        Transcribe Speech using Google Speech API

        Parameters
        ----------
        language: str
            Language Code, See: https://cloud.google.com/speech/docs/languages
        sample_rate: int
            Input Audio Sample Rate
        max_alternatives: int
            Maximum Number of Alternatives Google will provide
        """
        super(GoogleASR, self).__init__()

        self._sample_rate = sample_rate
        self._language = language
        self._max_alternatives = max_alternatives

        self._log = logging.getLogger("{} ({})".format(self.__class__.__name__, self._language))
        self._log.debug("Booted")

    def transcribe(self, audio, hints=()):
        """
        Transcribe Speech in Audio

        Parameters
        ----------
        audio: numpy.ndarray

        Returns
        -------
        transcript: List
            List of (<transcript>, <confidence>) pairs
        """
        response = speech.SpeechClient().recognize(speech.types.RecognitionConfig(
                encoding = speech.enums.RecognitionConfig.AudioEncoding.LINEAR16, sample_rate_hertz = self._sample_rate,
                language_code = self._language, max_alternatives = self._max_alternatives,
                speech_contexts = [speech.types.SpeechContext(phrases=hints)]),
            speech.types.RecognitionAudio(content=audio.tobytes()))
        hypotheses = []

        for result in response.results:
            for alternative in result.alternatives:
                hypotheses.append([alternative.transcript, alternative.confidence])

        if hypotheses:
            self._log.info("[{:3.0%}] {}".format(hypotheses[0][1], hypotheses[0][0]))

        return hypotheses