from pepper.framework.abstract.text_to_speech import AbstractTextToSpeech
import logging


class SystemTextToSpeech(AbstractTextToSpeech):
    def __init__(self):
        """System Text to Speech"""

        super(AbstractTextToSpeech, self).__init__()
        self._log = logging.getLogger(self.__class__.__name__)
        self._log.debug("Booted")

    def say(self, text):
        """
        Say something through Text to Speech

        Parameters
        ----------
        text: str
        """
        self._log.info(text)