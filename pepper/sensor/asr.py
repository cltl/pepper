from __future__ import unicode_literals

from pepper import logger

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


class AbstractASR(object):
    def __init__(self, language):
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
        return self._language

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
        super(GoogleASR, self).__init__(language)

        self._sample_rate = sample_rate
        self._max_alternatives = max_alternatives

        self._log.debug("Booted")

    def transcribe(self, audio, hints=()):
        """
        Transcribe Speech in Audio

        Parameters
        ----------
        audio: numpy.ndarray

        Returns
        -------
        hypotheses: List[ASRHypothesis]
        """
        response = speech.SpeechClient().recognize(speech.types.RecognitionConfig(
                encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=self._sample_rate,
                language_code=self._language,
                max_alternatives=self._max_alternatives,
                speech_contexts=[speech.types.SpeechContext(phrases=hints)]),
            speech.types.RecognitionAudio(content=audio.tobytes()))

        hypotheses = []
        for result in response.results:
            for alternative in result.alternatives:
                hypotheses.append(ASRHypothesis(alternative.transcript, alternative.confidence))

        if not self.language.startswith('en'):
            # Translate Input Speech into English if not already in English
            client = translate_v2.Client()
            new_hypotheses = [ASRHypothesis(client.translate(hypothesis.transcript)['translatedText'], hypothesis.confidence) for hypothesis in hypotheses]
            if hypotheses: self._log.debug("[{:3.0%}] {} -> {}".format(hypotheses[0].confidence, hypotheses[0].transcript, new_hypotheses[0].transcript))
            return new_hypotheses

        else:
            if hypotheses: self._log.debug("[{:3.0%}] {}".format(hypotheses[0].confidence, hypotheses[0].transcript))
            return hypotheses
