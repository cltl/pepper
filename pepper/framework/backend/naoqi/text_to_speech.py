from __future__ import unicode_literals

from pepper.framework.abstract.text_to_speech import AbstractTextToSpeech


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

        self._log.debug("Booted")

    def say(self, text, animation=None):
        """
        Say something through Text to Speech

        Parameters
        ----------
        text: str
        animation: str
        """
        self._log.info(text)

        if animation:
            self._service.say("^startTag({1}){0}^waitTag({1})".format(text, animation))
        else:
            self._service.say(text)