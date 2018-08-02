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
    def __init__(self, language='en-GB', sample_rate=16000, max_alternatives = 10, phrases=()):
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
        phrases: tuple of str
            Phrases or words to add to Google Speech's Vocabulary
        """
        super(GoogleASR, self).__init__()

        self._config = speech.types.RecognitionConfig(
            encoding = speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz = sample_rate,
            language_code = language,
            max_alternatives = max_alternatives,
            speech_contexts=[speech.types.SpeechContext(
                phrases=phrases
            )]
        )

        self._log = logging.getLogger(self.__class__.__name__)
        self._log.debug("Booted")

    def transcribe(self, audio):
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
        response = speech.SpeechClient().recognize(self._config,speech.types.RecognitionAudio(content=audio.tobytes()))
        hypotheses = []

        for result in response.results:
            for alternative in result.alternatives:
                hypotheses.append([alternative.transcript, alternative.confidence])

        if hypotheses:
            self._log.debug(hypotheses[0][0])

        return hypotheses
