from pepper.framework import *
from pepper.knowledge import Wikipedia, Wolfram, animations
from pepper.language import Utterance

from .responder import Responder, ResponderType

import re

from typing import Optional, Union, Tuple, Callable


class WikipediaResponder(Responder):
    WEB_CUE = [
        "can you search ",
        "can you look up ",
        "can you query ",
    ]

    @property
    def type(self):
        return ResponderType.Internet

    @property
    def requirements(self):
        return [TextToSpeechComponent]

    def respond(self, utterance, app):
        # type: (Utterance, Union[TextToSpeechComponent]) -> Optional[Tuple[float, Callable]]

        for que in self.WEB_CUE:
            if utterance.transcript.lower().startswith(que):

                result = Wikipedia.query(utterance.transcript.lower().replace(que, ""))

                if result:
                    # Get Answer and Image URL from Wikipedia Query
                    answer, url = result

                    # Take Summary (a.k.a. First Sentence) from Wikipedia Query
                    answer = re.split('[.\n]', answer)[0]

                    # Return Result
                    return 1.0, lambda: app.say(answer, animation=animations.EXPLAIN)

                break


class WolframResponder(Responder):
    WEB_CUE = [
        "can you search ",
        "can you look up ",
        "can you query ",
    ]

    def __init__(self):
        self._wolfram = Wolfram()

    @property
    def type(self):
        return ResponderType.PAID

    @property
    def requirements(self):
        return [TextToSpeechComponent]

    def respond(self, utterance, app):
        # type: (Utterance, Union[TextToSpeechComponent]) -> Optional[Tuple[float, Callable]]

        for que in self.WEB_CUE:
            if utterance.transcript.lower().startswith(que):

                transcript = utterance.transcript.lower().replace(que, "")

                if self._wolfram.is_query(transcript):
                    result = self._wolfram.query(transcript)

                    if result:
                        return 1.0, lambda: app.say(result, animations.EXPLAIN)

                break
