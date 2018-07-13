from pepper.framework.abstract.text_to_speech import AbstractTextToSpeech
import logging


class NaoqiTextToSpeech(AbstractTextToSpeech):

    SERVICE = "ALAnimatedSpeech"

    def __init__(self, session):
        super(NaoqiTextToSpeech, self).__init__()
        self._service = session.service(NaoqiTextToSpeech.SERVICE)

        self._log = logging.getLogger(self.__class__.__name__)
        self._log.debug("Booted")

    def say(self, text):
        self._log.info(text)
        self._service.say(text)