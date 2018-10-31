from pepper.framework.abstract import AbstractComponent
from pepper import config


class SpeechKeyboard(AbstractComponent):
    def __init__(self, backend):
        super(SpeechKeyboard, self).__init__(backend)

    def on_transcript(self, hypotheses, audio):
        pass