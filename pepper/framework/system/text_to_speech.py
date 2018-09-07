from pepper.framework.abstract.text_to_speech import AbstractTextToSpeech

from google.cloud import texttospeech
from playsound import playsound

import logging
from random import getrandbits
from time import sleep
import os


class SystemTextToSpeech(AbstractTextToSpeech):

    def __init__(self):
        """System Text to Speech"""

        super(AbstractTextToSpeech, self).__init__()

        self._client = texttospeech.TextToSpeechClient()
        self._voice = texttospeech.types.VoiceSelectionParams(
            language_code='en-US',
            name="en-US-Wavenet-F")

        # Select the type of audio file you want returned
        self._audio_config = texttospeech.types.AudioConfig(
            audio_encoding=texttospeech.enums.AudioEncoding.MP3)

        self._busy = False

        self._log = logging.getLogger(self.__class__.__name__)
        self._log.debug("Booted")

    def say(self, text):
        """
        Say something through Text to Speech

        Parameters
        ----------
        text: str
        """

        while self._busy: sleep(0.1)
        self._busy = True

        self._log.info(text)

        synthesis_input = texttospeech.types.SynthesisInput(text=text)
        response = self._client.synthesize_speech(synthesis_input, self._voice, self._audio_config)

        file_hash = "{}.mp3".format(str(getrandbits(128)))
        with open(file_hash, 'wb') as out:
            out.write(response.audio_content)

        playsound(file_hash)
        os.remove(file_hash)

        self._busy = False


