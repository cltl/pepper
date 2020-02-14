from .responder import Responder, ResponderType
from pepper.framework import *
from pepper.language import Utterance
from pepper.knowledge import animations

from random import choice

from typing import Optional, Union, Tuple, Callable


class BrexitResponder(Responder):

    @property
    def type(self):
        return ResponderType.Topic

    @property
    def requirements(self):
        return [TextToSpeechComponent]

    def respond(self, utterance, app):
        # type: (Utterance, Union[TextToSpeechComponent]) -> Optional[Tuple[float, Callable]]

        transcript = utterance.transcript.lower()

        if all(key in transcript for key in ['you', 'think', 'brexit']):
            # -> What do you think about the brexit?
            return 1.0, lambda: app.say("I just know what is written in the news and what people tell me. "
                                        "I don't think I'm smart enough yet to make up my own mind about the Brexit.")
        elif all(key in transcript for key in ['you', 'know', 'brexit']):
            # -> What do you know about the brexit?
            return 1.0, lambda: app.say("I know the Brexit is about politics! I don't know a lot about politics!")
        elif all(key in transcript for key in ['brexit', 'you']):
            # -> Brexit for Robots?
            return 1.0, lambda: app.say("I just hope I can still talk to and learn from my British Robot friends!")