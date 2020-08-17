from __future__ import unicode_literals

import re
import urllib
from threading import Timer

from typing import Optional

from pepper import config
from pepper.framework.abstract.component import AbstractComponent
from pepper.framework.component import ContextComponent, TextToSpeechComponent, SpeechRecognitionComponent


class SubtitlesComponent(AbstractComponent):

    SUBTITLES_URL = "https://bramkraai.github.io/subtitle?text={}"
    SUBTITLES_TIMEOUT = 15

    def __init__(self):
        # type: () -> None
        super(SubtitlesComponent, self).__init__()

        self._log.info("Initializing SubtitlesComponent")

        self._subtitles_timeout_timer = None  # type: Optional[Timer]

        self.require(SubtitlesComponent, TextToSpeechComponent)
        self.require(SubtitlesComponent, SpeechRecognitionComponent)

    def say(self, text, animation=None, block=False):
        # type: (str, str, bool) -> None
        self._show_subtitles('{}:/"{}"'.format(config.NAME, text))
        super(SubtitlesComponent, self).say(text, animation, block)

    def on_transcript(self, hypotheses, audio):

        speaker = "Human"

        try:
            if isinstance(self, ContextComponent) and self.context.chatting:
                speaker = self.context.chat.speaker
        except AttributeError as e:
            pass

        self._show_subtitles('{}:/"{}"'.format(speaker, hypotheses[0].transcript))
        super(SubtitlesComponent, self).on_transcript(hypotheses, audio)

    def _show_subtitles(self, text):

        # Stop Timeout Timer if running
        if self._subtitles_timeout_timer: self._subtitles_timeout_timer.cancel()

        # Show Subtitles
        text_websafe = urllib.quote(''.join([i for i in re.sub(r'\\\\\S+\\\\', "", text) if ord(i) < 128]))
        self.backend.tablet.show(self.SUBTITLES_URL.format(text_websafe))

        # Start Timeout Timer
        self._subtitles_timeout_timer = Timer(self.SUBTITLES_TIMEOUT, self.backend.tablet.hide)
        self._subtitles_timeout_timer.start()
