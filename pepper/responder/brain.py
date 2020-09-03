import re
from random import choice

from typing import Optional, Union, Tuple, Callable

from pepper import logger
from pepper.framework.component import TextToSpeechComponent, BrainComponent
from pepper.knowledge import sentences, animations
from pepper.language import Utterance
from pepper.language import UtteranceType
from pepper.language.generation.reply import reply_to_question
from pepper.language.generation.thoughts_phrasing import phrase_thoughts
from .responder import Responder, ResponderType


class BrainResponder(Responder):
    def __init__(self):
        self._log = logger.getChild(self.__class__.__name__)

    @property
    def type(self):
        return ResponderType.Brain

    @property
    def requirements(self):
        return [TextToSpeechComponent, BrainComponent]

    def respond(self, utterance, app):
        # type: (Utterance, Union[TextToSpeechComponent, BrainComponent]) -> Optional[Tuple[float, Callable]]

        try:
            utterance.analyze()

            self._log.debug("TRIPLE: {}".format(utterance.triple))

            if utterance.triple is not None:
                brain_response_statement = []
                brain_response_question = []

                if utterance.type == UtteranceType.QUESTION:
                    brain_response_question = app.brain.query_brain(utterance)
                    reply = reply_to_question(brain_response_question)
                    self._log.info("REPLY to question: {}".format(reply))
                else:
                    brain_response_statement = app.brain.update(utterance, reason_types=True)  # Searches for types in dbpedia
                    reply = phrase_thoughts(brain_response_statement, True, True, True)
                    self._log.info("REPLY to statement: {}".format(reply))

                if (isinstance(reply, str) or isinstance(reply, unicode)) and reply != "":
                    # Return Score and Response
                    # Make sure to not execute the response here, but just to return the response function
                    return 1.0, lambda: app.say(re.sub(r"[\s+_]", " ", reply))
                elif brain_response_statement:
                    # Thank Human for the Data!
                    return 1.0, lambda: app.say("{} {}".format(choice([choice(sentences.THANK), choice(sentences.HAPPY)]),
                                                               choice(sentences.PARSED_KNOWLEDGE)), animations.HAPPY)
                elif brain_response_question:
                    # Apologize to human for not knowing
                    return 1.0, lambda: app.say("{} {}".format(choice(sentences.SORRY),
                                                               choice(sentences.NO_ANSWER)), animations.ASHAMED)

        except Exception as e:
            self._log.error(e)
