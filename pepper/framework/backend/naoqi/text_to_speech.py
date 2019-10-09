from __future__ import unicode_literals

from pepper.framework.abstract.text_to_speech import AbstractTextToSpeech
from pepper.config import NAOQI_SPEECH_SPEED, SUBTITLES_URL, SUBTITLES_TIMEOUT, SUBTITLES

import qi

from threading import Timer

import urllib
import re

from typing import Union, Optional


class NAOqiTextToSpeech(AbstractTextToSpeech):
    """
    NAOqi Text to Speech

    Parameters
    ----------
    session: qi.Session
        Qi Application Session
    """

    SERVICE = "ALAnimatedSpeech"

    def __init__(self, session, language):
        # type: (qi.Session, str) -> None
        super(NAOqiTextToSpeech, self).__init__(language)

        # Subscribe to NAOqi Text to Speech Service
        self._service = session.service(NAOqiTextToSpeech.SERVICE)
        self._tablet_service = session.service("ALTabletService")
        self._tablet_timer = None

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

        if SUBTITLES:
            url = SUBTITLES_URL.format(urllib.quote(self._make_ascii(re.sub(r'\\\\\S+\\\\', "", text))))
            self._tablet_service.showWebview(url)

        if animation:
            self._service.say(r"\\rspd={2}\\^startTag({1}){0}^stopTag({1})".format(text, animation, NAOQI_SPEECH_SPEED))
        else:
            self._service.say(r"\\rspd={1}\\{0}".format(text, NAOQI_SPEECH_SPEED))

        if SUBTITLES and SUBTITLES_TIMEOUT:
            if self._tablet_timer: self._tablet_timer.cancel()
            self._tablet_timer = Timer(SUBTITLES_TIMEOUT, self._tablet_service.hide)
            self._tablet_timer.start()

    def _make_ascii(self, text):
        return ''.join([i for i in text if ord(i) < 128])
