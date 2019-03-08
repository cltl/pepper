from pepper.framework import *
from pepper.knowledge import Wikipedia, animations
from pepper.language import Utterance

from .responder import Responder, ResponderType

import re

from typing import Optional, Union, Tuple, Callable


class WikipediaResponder(Responder):
    @property
    def type(self):
        return ResponderType.Internet

    @property
    def requirements(self):
        return [TextToSpeechComponent]

    def respond(self, utterance, app):
        # type: (Utterance, Union[TextToSpeechComponent]) -> Optional[Tuple[float, Callable]]

        result = Wikipedia.query(utterance.transcript)

        if result:

            # Get Answer and Image URL from Wikipedia Query
            answer, url = result

            # Take Summary (a.k.a. First Sentence) from Wikipedia Query
            answer = re.split('[.\n]', answer)[0]

            # Return Result
            return 1.0, lambda: app.say(answer, animation=animations.EXPLAIN)
