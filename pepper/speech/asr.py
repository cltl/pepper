from google.cloud import speech
import numpy as np
from scipy.io import wavfile
import re


class ASR(object):
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
            List of (<transcript>, <confidence>) pairs
        """
        raise NotImplementedError()


class GoogleASR(ASR):
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
                hypotheses.append([
                    alternative.transcript,
                    alternative.confidence
                ])
        return hypotheses


class GoogleWordASR(ASR):
    def __init__(self, language='en-GB', sample_rate=16000, max_alternatives = 10, phrases=()):
        """
        Transcribe Speech using Google Speech API and provide Word Timings

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
        super(GoogleWordASR, self).__init__()

        self._config = speech.types.RecognitionConfig(
            encoding = speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz = sample_rate,
            language_code = language,
            max_alternatives = max_alternatives,
            enable_word_time_offsets=True,
            speech_contexts=[speech.types.SpeechContext(
                phrases=phrases
            )]
        )

    def transcribe(self, audio):
        """
        Transcribe Speech in Audio

        Parameters
        ----------
        audio: numpy.ndarray

        Returns
        -------
        transcript: List
            List of (<transcript>, <confidence>, <word timings>) pairs
        """
        response = speech.SpeechClient().recognize(self._config,speech.types.RecognitionAudio(content=audio.tobytes()))
        hypotheses = []

        for result in response.results:
            for alternative in result.alternatives:
                hypotheses.append([
                    alternative.transcript,
                    alternative.confidence,
                    [[word.word,
                      word.start_time.seconds + word.start_time.nanos * 1E-9,
                      word.end_time.seconds + word.end_time.nanos * 1E-9,
                      ] for word in alternative.words]
                ])
        return hypotheses


class NameASR(object):

    NAMES = ["Leolani", "Piek", "Selene", "Lenka", "Bram"]
    LANGUAGES = ['en-GB', 'nl-NL', 'es-ES']

    NAME_REGEX = "([A-Z]\w+)"

    def __init__(self, sample_rate=16000, max_alternatives=10, hints = ("My name is {}", "I'm {}", "I am {}")):
        self._sample_rate = sample_rate
        self.hints = hints

        self.phrases = [hint.format(name) for name in self.NAMES for hint in self.hints]
        self.hint_regex = [hint.format(self.NAME_REGEX) for hint in self.hints]

        self.asr = [GoogleASR(language, sample_rate, max_alternatives, self.phrases) for language in self.LANGUAGES]

    def transcribe(self, audio):

        name_match, name_confidence = None, 0

        for asr in self.asr:
            for transcript, confidence in asr.transcribe(audio):
                for hint in self.hint_regex:
                    name = re.findall(hint.lower(), transcript.lower())

                    if name:
                        name = name[0].title()

                        if name in self.NAMES:
                            return name, 1
                        elif confidence > name_confidence:
                            name_match = name
                            name_confidence = confidence

        return name_match, name_confidence

