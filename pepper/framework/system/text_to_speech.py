from pepper.framework.abstract.text_to_speech import AbstractTextToSpeech
from pepper import config

from google.cloud import texttospeech, translate_v2
from playsound import playsound

from random import getrandbits
from time import sleep
import os


class SystemTextToSpeech(AbstractTextToSpeech):

    ROOT = os.path.join(config.PROJECT_ROOT, 'tmp', 'speech')

    def __init__(self, language):
        """
        Parameters
        ----------
        language: str
            Language Code, See: https://cloud.google.com/speech/docs/languages
        """
        super(SystemTextToSpeech, self).__init__(language)

        if not os.path.exists(self.ROOT): os.makedirs(self.ROOT)

        self._client = texttospeech.TextToSpeechClient()
        self._voice = texttospeech.types.VoiceSelectionParams(language_code=language)

        # Select the type of audio file you want returned
        self._audio_config = texttospeech.types.AudioConfig(audio_encoding=texttospeech.enums.AudioEncoding.MP3)

        self._busy = False

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

        if 'en-' not in self.language:
            new_text = translate_v2.Client().translate(text, target_language=self.language)['translatedText']
            self._log.info("{} <- {}".format(new_text, text))
            text = new_text
        else:
            self._log.info(text)

        synthesis_input = texttospeech.types.SynthesisInput(text=text)
        response = self._client.synthesize_speech(synthesis_input, self._voice, self._audio_config)

        file_hash = os.path.join(self.ROOT, "{}.mp3".format(str(getrandbits(128))))
        with open(file_hash, 'wb') as out:
            out.write(response.audio_content)

        playsound(file_hash)
        os.remove(file_hash)

        self._busy = False


