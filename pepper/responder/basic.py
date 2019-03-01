from pepper.framework import TextToSpeechComponent
from pepper.language import Utterance
from .responder import Responder, ResponderType
from pepper.knowledge import animations

import re

from typing import Optional, Union, Tuple, Callable

from random import choice


class GreetingResponder(Responder):

    GREETINGS = [
        "Yo",
        "Hey!",
        "Hello!",
        "Hi!",
        "Good Day",
        "How's it going?",
        "How are you doing?",
        "What's up?",
        "What's new?",
        "What's going on?",
        "What's up?",
        "Good to see you!",
        "Nice to see you!",
    ]

    _GREETINGS_STRIPPED = [re.sub('[!?]', '', greeting.lower()) for greeting in GREETINGS]

    @property
    def type(self):
        return ResponderType.Conversational

    @property
    def requirements(self):
        return [TextToSpeechComponent]

    def respond(self, utterance, app):
        # type: (Utterance, Union[TextToSpeechComponent]) -> Optional[Tuple[float, Callable]]

        if utterance.transcript.lower() in self._GREETINGS_STRIPPED:
            return 1, lambda: app.say("{}, {}!".format(choice(self.GREETINGS), utterance.chat.speaker), animations.HI)


class GoodbyeResponder(Responder):

    GOODBYES = [
        "Bye",
        "Bye Bye",
        "See you",
        "See you later",
        "Goodbye",
        "Good Bye",
        "Have a nice day",
        "Nice having talked to you",
    ]

    _GOODBYES_STRIPPED = [re.sub('[!?]', '', goodbye.lower()) for goodbye in GOODBYES]

    @property
    def type(self):
        return ResponderType.Conversational

    @property
    def requirements(self):
        return [TextToSpeechComponent]

    def respond(self, utterance, app):
        # type: (Utterance, Union[TextToSpeechComponent]) -> Optional[Tuple[float, Callable]]
        if utterance.transcript.lower() in self._GOODBYES_STRIPPED:
            return 1, lambda: app.say("{}, {}!".format(choice(self.GOODBYES), utterance.chat.speaker), animations.BOW)
