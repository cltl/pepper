from pepper.framework.abstract.text_to_speech import AbstractTextToSpeech
import logging


class NaoqiTextToSpeech(AbstractTextToSpeech):

    SERVICE = "ALAnimatedSpeech"

    def __init__(self, session, language):
        """
        Naoqi Text to Speech

        Parameters
        ----------
        session: qi.Session
            Qi Application Session
        """
        super(NaoqiTextToSpeech, self).__init__(language)

        # Subscribe to Naoqi Text to Speech Service
        self._service = session.service(NaoqiTextToSpeech.SERVICE)

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
        self._service.say(text)