from __future__ import unicode_literals

from pepper.framework.abstract.text_to_speech import AbstractTextToSpeech
from pepper.config import  NAOQI_SPEECH_SPEED

import qi

from typing import Union, Optional


class NAOqiTextToSpeech(AbstractTextToSpeech):

    SERVICE = "ALAnimatedSpeech"

    def __init__(self, session, language):
        # type: (qi.Session, str) -> None
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
        # type: (Union[str, unicode], Optional[str]) -> None
        """
        Say something through Text to Speech

        Parameters
        ----------
        text: str
        animation: str
        """

        text = text.replace('...', r'\\pau=1000\\')

        if animation:
            self._service.say(r"\\rspd={2}\\^startTag({1}){0}^stopTag({1})".format(text, animation, NAOQI_SPEECH_SPEED))
        else:
            self._service.say(r"\\rspd={1}\\{0}".format(text, NAOQI_SPEECH_SPEED))
