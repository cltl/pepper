from .responder import Responder, ResponderType
from pepper.framework import *
from pepper.language import Utterance
from pepper.knowledge import animations

from random import choice

from typing import Optional, Union, Tuple, Callable


class BrexitResponder(Responder):

    BREXIT_ELOQUENCE = [
        "Brexit is indeed a complex topic."
    ]

    @property
    def type(self):
        return ResponderType.Topic

    @property
    def requirements(self):
        return [TextToSpeechComponent]

    def respond(self, utterance, app):
        # type: (Utterance, Union[TextToSpeechComponent]) -> Optional[Tuple[float, Callable]]

        transcript = utterance.transcript.lower()

        # 'Eloquence' Fallback
        if "brexit" in transcript:
            return 1.0, lambda: app.say(choice(self.BREXIT_ELOQUENCE), animations.AFFIRMATIVE)