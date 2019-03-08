from pepper.framework import *
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

        for greeting in self._GREETINGS_STRIPPED:
            if utterance.transcript.lower().startswith(greeting):
                return 1, lambda: app.say(text="{}, {}!".format(choice(self.GREETINGS), utterance.chat.speaker),
                                          animation=animations.HI)


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

        for goodbye in self._GOODBYES_STRIPPED:
            if utterance.transcript.lower().startswith(goodbye):
                return 1, lambda: app.say(text="{}, {}!".format(choice(self.GOODBYES), utterance.chat.speaker),
                                          animation=animations.BOW)


class ThanksResponder(Responder):

    THANKS = [
        "thank you",
        "thanks",
        "appreciate",
        "cheers",
    ]

    THANKS_REPLY = [
        "You're welcome",
        "No problem",
        "Glad to be at service",
        "Anytime",
    ]

    @property
    def type(self):
        return ResponderType.Conversational

    @property
    def requirements(self):
        return [TextToSpeechComponent]

    def respond(self, utterance, app):
        # type: (Utterance, Union[TextToSpeechComponent]) -> Optional[Tuple[float, Callable]]
        for thanks in self.THANKS:
            if thanks in utterance.transcript.lower():
                return 1, lambda: app.say(text="{}, {}!".format(choice(self.THANKS_REPLY), utterance.chat.speaker),
                                          animation=animations.ENTHUSIASTIC)


class AffirmationResponder(Responder):

    AFFIRMATION = [
        "yes",
        "yeah",
        "correct",
        "alright",
        "right",
        "great",
        "true",
        "good",
        "well",
        "correctamundo",
        "splendid",
        "indeed",
        "superduper",
        "wow",
        "amazing"
    ]

    HAPPY = [
        "Nice!",
        "Cool!",
        "Great!",
        "Wow!",
        "Superduper!",
        "Amazing!",
        "I like it!",
        "That makes my day!",
        "Incredible",
        "Mesmerizing"
    ]

    @property
    def type(self):
        return ResponderType.Conversational

    @property
    def requirements(self):
        return [TextToSpeechComponent]

    def respond(self, utterance, app):
        # type: (Utterance, Union[TextToSpeechComponent]) -> Optional[Tuple[float, Callable]]
        for token in utterance.tokens:
            if token in self.AFFIRMATION:
                return 1, lambda: app.say(choice(self.HAPPY), animations.HAPPY)


class NegationResponder(Responder):

    NEGATION = [
        "no",
        "nope",
        "incorrect",
        "wrong",
        "false",
        "bad",
        "stupid"
    ]

    SORRY = [
        "Sorry!",
        "I am sorry!",
        "Forgive me!",
        "My apologies!",
        "My humble apologies!",
        "How unfortunate!",
        "My mistake",
    ]

    @property
    def type(self):
        return ResponderType.Conversational

    @property
    def requirements(self):
        return [TextToSpeechComponent]

    def respond(self, utterance, app):
        # type: (Utterance, Union[TextToSpeechComponent]) -> Optional[Tuple[float, Callable]]
        for token in utterance.tokens:
            if token in self.NEGATION:
                return 1, lambda: app.say(choice(self.SORRY), animations.HAPPY)
