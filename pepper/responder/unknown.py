from pepper.framework import *
from pepper.language import Utterance
from .responder import Responder, ResponderType
from pepper.knowledge import animations, sentences

from typing import Optional, Union, Tuple, Callable

from random import choice, random


class UnknownResponder(Responder):

    ELOQUENCE = sentences.ELOQUENCE

    HEARD = ["I think you said", "I heard", "I picked up", "I'm guessing you told me"]
    NOT_UNDERSTAND = ["I don't know what it means", "I don't understand it", "I couldn't parse it",
                      "I have no idea about it", "I have no clue", "this goes above my robot-skills",
                      "I find this quite difficult to understand", "It doesn't ring any bells"]

    @property
    def type(self):
        return ResponderType.Unknown

    @property
    def requirements(self):
        return [TextToSpeechComponent]

    def respond(self, utterance, app):
        # type: (Utterance, Union[TextToSpeechComponent]) -> Optional[Tuple[float, Callable]]

        if len(utterance.tokens) < 10 and random() > 0.8:
            return 1, lambda: app.say(choice(self.ELOQUENCE), animation=choice([animations.COOL, animations.COGITATE]))
        else:
            return 1, lambda: app.say(
                "{}: {}, but {}!".format(choice(self.HEARD), utterance.transcript, choice(self.NOT_UNDERSTAND)),
                choice([animations.NOT_KNOW,animations.UNFAMILIAR, animations.UNCOMFORTABLE, animations.SHAMEFACED]))
