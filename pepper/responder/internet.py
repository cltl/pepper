from pepper import logger
import re

from typing import Optional, Union, Tuple, Callable
from random import random

from pepper.framework.component import TextToSpeechComponent
from pepper.knowledge import Wikipedia, Wolfram, animations
from pepper.language import Utterance
from .responder import Responder, ResponderType

class WikipediaResponder(Responder):
    WEB_CUE = [
        "can you search ",
        "can you look up ",
        "can you query ",
        "google ",
        "what does the internet say about ",
        "quick question ",
        "can you find out ",
        "can you google ",
    ]

    def __init__(self):
        self._wolfram = Wolfram()
        self._log = logger.getChild(self.__class__.__name__)

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
        "google ",
        "what does the internet say about ",
        "quick question ",
        "can you find out ",
        "can you google ",
        "search ",
        "go online ",
        "find me ",
    ]

    def __init__(self):
        self._wolfram = Wolfram()
        self._log = logger.getChild(self.__class__.__name__)

    @property
    def type(self):
        return ResponderType.PAID

    @property
    def requirements(self):
        return [TextToSpeechComponent]

    def respond(self, utterance, app):
        # type: (Utterance, Union[TextToSpeechComponent]) -> Optional[Tuple[float, Callable]]

        transcript = utterance.transcript.lower().strip()
        wellformed_query = self._wolfram.is_query(transcript)

        for que in self.WEB_CUE:
            # if transcript.lower().startswith(que) or wellformed_query:
            if transcript.find(que.strip()) >= 0 or wellformed_query:
                print("Web cue: ", que, transcript, transcript.find(que.strip()), wellformed_query)

                transcript = transcript.replace(que, "")

                if self._wolfram.is_query(transcript):
                    result = self._wolfram.query(transcript)

                    if result:
                        return 1.0, lambda: app.say(result, animations.EXPLAIN)

                else:
                    self._log.info("Ill-formed query for Wolfram : {}".format(transcript))

                break
