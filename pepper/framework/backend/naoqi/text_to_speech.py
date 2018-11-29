from __future__ import unicode_literals

from pepper.framework.abstract.text_to_speech import AbstractTextToSpeech


class NAOqiTextToSpeech(AbstractTextToSpeech):

    SERVICE = "ALAnimatedSpeech"

    def __init__(self, session, language):
        """
        NAOqi Text to Speech

        Parameters
        ----------
        session: qi.Session
            Qi Application Session
        """
        super(NAOqiTextToSpeech, self).__init__(language)

        # Subscribe to NAOqi Text to Speech Service
        self._service = session.service(NAOqiTextToSpeech.SERVICE)

        self._log.debug("Booted")

    def on_text_to_speech(self, text, animation=None):
        """
        Say something through Text to Speech

        Parameters
        ----------
        text: str
        animation: str
        """

        if animation:
            self._service.say("^startTag({1}){0}^stopTag({1})".format(text, animation))
        else:
            self._service.say(text)