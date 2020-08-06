from random import choice

from typing import Optional, Union, Tuple, Callable

from pepper.framework.component import TextToSpeechComponent
from pepper.knowledge import QnA
from pepper.language import Utterance
from .responder import Responder, ResponderType


class QnAResponder(Responder):

    ADDRESS = [
        "Well",
        "You see",
        "See",
        "Look",
        "I'll tell you",
        "Guess what",
        "Ok",
    ]

    def __init__(self):
        super(QnAResponder, self).__init__()
        self._qna = QnA()

    @property
    def type(self):
        return ResponderType.Personal

    @property
    def requirements(self):
        return [TextToSpeechComponent]

    def respond(self, utterance, app):
        # type: (Utterance, Union[TextToSpeechComponent]) -> Optional[Tuple[float, Callable]]

        result = self._qna.query(utterance.transcript)

        if result:
            score, answer = result
            return score, lambda: app.say("{}, {}, {}".format(choice(self.ADDRESS), utterance.chat.speaker, answer))
