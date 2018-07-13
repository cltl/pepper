from pepper.framework.abstract.text_to_speech import AbstractTextToSpeech
import logging


class SystemTextToSpeech(AbstractTextToSpeech):
    def __init__(self):
        super(AbstractTextToSpeech, self).__init__()
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Booted")

    def say(self, text):
        self._logger.info(text)