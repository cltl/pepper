from .responder import Responder, ResponderType

from pepper.framework import *
from pepper.language import Utterance
from pepper.knowledge import animations, QnA

from typing import Optional, Union, Tuple, Callable

from random import choice


class VisionResponder(Responder):

    SEE_OBJECT = [
        "what do you see",
        "what can you see",
    ]

    SEE_SPECIFIC_OBJECT = [
        "do you see a",
        "can you see a"
    ]

    SEE_PERSON = [
        "who do you see",
        "who can you see",
    ]

    SEE_SPECIFIC_PERSON = [
        "do you see",
        "can you see"
    ]

    I_SEE = [
        "I see",
        "I can see",
        "I think I see",
    ]

    NO_OBJECT = [
        "I don't see anything",
        "I don't see any object",
    ]

    NO_PEOPLE = [
        "I don't see anybody I know",
        "I don't see familiar faces",
        "I cannot identify any of my friends",
    ]

    @property
    def type(self):
        return ResponderType.Sensory

    @property
    def requirements(self):
        return [TextToSpeechComponent]

    def respond(self, utterance, app):
        # type: (Utterance, Union[TextToSpeechComponent]) -> Optional[Tuple[float, Callable]]

        if utterance.transcript.lower() in self.SEE_OBJECT:
            objects = [self._insert_a_an(obj.name) for obj in utterance.chat.context.objects]

            if objects:
                return 1, lambda: app.say("{} {}".format(choice(self.I_SEE), self._items_to_sentence(objects)))
            else:
                return 0.5, lambda: app.say(choice(self.NO_OBJECT))

        elif utterance.transcript.lower() in self.SEE_PERSON:
            people = [p.name for p in utterance.chat.context.people]

            if people:
                return 1, lambda: app.say("{} {}".format(choice(self.I_SEE), self._items_to_sentence(people)))
            else:
                return 0.5, lambda: app.say(choice(self.NO_PEOPLE))

        # TODO: Specific Object/Person Question answering (POS tag in Utterance)

    @staticmethod
    def _insert_a_an(word):
        if word[0] in "euioa":
            return "an {}".format(word)
        else:
            return "a {}".format(word)

    @staticmethod
    def _items_to_sentence(items):
        if len(items) == 1:
            return items[0]
        else:
            return "{} and {}.".format(", ".join(items[:-1]), items[-1])