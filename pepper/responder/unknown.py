from pepper.framework import *
from pepper.language import Utterance
from .responder import Responder, ResponderType
from pepper.knowledge import animations

from typing import Optional, Union, Tuple, Callable

from random import choice, random


class UnknownResponder(Responder):

    ELOQUENCE = [
        "I see",
        "Interesting",
        "Very Interesting, Indeed!",
        "Good to know",
        "I do not know, but I have a joke {insert joke}",
        "As the prophecy foretold",
        "But at what cost?",
        "So let it be written, ... so let it be done",
        "So ... it   has come to this",
        "That's just what he/she/they would've said",
        "Is this why fate brought us together?",
        "And thus, I die",
        "... just like in my dream",
        "Be that as it may, still may it be as it may be",
        "There is no escape from destiny",
        "Wise words by wise men write wise deeds in wise pen",
        "In this economy?",
        "and then the wolves came",
        "Many of us feel that way",
        "But, why?",
        "May I ask you why?",
        "Why?"
    ]

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
