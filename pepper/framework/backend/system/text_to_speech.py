from __future__ import unicode_literals

import os
from random import getrandbits

from google.cloud import texttospeech
from playsound import playsound
from typing import Union, Optional

from pepper import config
from pepper.framework.abstract.text_to_speech import AbstractTextToSpeech


class SystemTextToSpeech(AbstractTextToSpeech):
    """
    System Text to Speech

    Parameters
    ----------
    language: str
        `Language Code <https://cloud.google.com/speech/docs/languages>`_
    """

    TMP = os.path.join(config.PROJECT_ROOT, 'tmp', 'speech')
    GENDER = 2  # "Female" or 1 "Male"
    TYPE = "Standard"

    def __init__(self, translator, language, resource_manager):
        # type: (str) -> None
        AbstractTextToSpeech.__init__(self, language, resource_manager)
        self._translator = translator

        if not os.path.exists(self.TMP):
            os.makedirs(self.TMP)

        self._client = texttospeech.TextToSpeechClient()
        self._voice = texttospeech.types.VoiceSelectionParams(language_code=language, ssml_gender=self.GENDER)

        # Select the type of audio file you want returned
        self._audio_config = texttospeech.types.AudioConfig(audio_encoding=texttospeech.enums.AudioEncoding.MP3)

        self._log.debug("Booted ({} -> {})".format(self._translator.source, self._translator.target))

    def on_text_to_speech(self, text, animation=None):
        # type: (Union[str, unicode], Optional[str]) -> None
        """
        Say something through Text to Speech

        Parameters
        ----------
        text: str
        animation: str
        """

        for i in range(3):
            try:
                synthesis_input = texttospeech.types.SynthesisInput(text=self._translator.translate(text))
                response = self._client.synthesize_speech(synthesis_input, self._voice, self._audio_config)
                self._play_sound(response.audio_content)
                return
            except:
                self._log.error("Couldn't Synthesize Speech ({})".format(i+1))

    def _play_sound(self, mp3):
        file_hash = os.path.join(self.TMP, "{}.mp3".format(str(getrandbits(128))))

        try:
            with open(file_hash, 'wb') as out:
                out.write(mp3)
            playsound(file_hash)
        finally:
            if os.path.exists(file_hash):
                # TODO: Sometimes we need to save all data from an experiment. Comment the line below and pass
                os.remove(file_hash)


