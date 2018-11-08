from __future__ import unicode_literals

from pepper.framework.abstract.text_to_speech import AbstractTextToSpeech
from pepper import config

from google.cloud import texttospeech, translate_v2
from playsound import playsound

from random import getrandbits
from time import sleep
import os


class SystemTextToSpeech(AbstractTextToSpeech):

    TMP = os.path.join(config.PROJECT_ROOT, 'tmp', 'speech')
    GENDER = 2  # "Female" or 1 "Male"
    TYPE = "Standard"

    def __init__(self, language):
        """
        Parameters
        ----------
        language: str
            Language Code, See: https://cloud.google.com/speech/docs/languages
        """
        super(SystemTextToSpeech, self).__init__(language)

        if not os.path.exists(self.TMP):
            os.makedirs(self.TMP)

        self._translate_client = None
        self._target_language = language[:2]

        if self._target_language != 'en':
            self._translate_client = translate_v2.Client(target_language=self._target_language)

        self._client = texttospeech.TextToSpeechClient()
        self._voice = texttospeech.types.VoiceSelectionParams(language_code=language, ssml_gender=self.GENDER)

        # Select the type of audio file you want returned
        self._audio_config = texttospeech.types.AudioConfig(audio_encoding=texttospeech.enums.AudioEncoding.MP3)

        self._log.debug("Booted")

    def on_text_to_speech(self, text, animation=None):
        """
        Say something through Text to Speech

        Parameters
        ----------
        text: str
        animation: str
        """
        synthesis_input = texttospeech.types.SynthesisInput(text=self.translate(text))
        response = self._client.synthesize_speech(synthesis_input, self._voice, self._audio_config)
        self._play_sound(response.audio_content)

    def translate(self, text):
        if self._translate_client is not None:
            return self._translate_client.translate(text, source_language='en')['translatedText']
        else:
            return text

    def _play_sound(self, mp3):
        file_hash = os.path.join(self.TMP, "{}.mp3".format(str(getrandbits(128))))

        try:
            with open(file_hash, 'wb') as out:
                out.write(mp3)
            playsound(file_hash)
        finally:
            if os.path.exists(file_hash):
                os.remove(file_hash)


