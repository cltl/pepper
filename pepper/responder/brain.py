from pepper.framework import *

from pepper.language import Utterance, utils
from pepper.language.generation import phrasing

from .responder import Responder, ResponderType
from pepper.language import analyze, UtteranceType

import re

from typing import Optional, Union, Tuple, Callable


class BrainResponder(Responder):
    @property
    def type(self):
        return ResponderType.Brain

    @property
    def requirements(self):

        # TODO: List all Components you need
        return [TextToSpeechComponent, BrainComponent]

    def respond(self, utterance, app):
        # type: (Utterance, Union[TextToSpeechComponent, BrainComponent]) -> Optional[Tuple[float, Callable]]

        try:

            print(utterance.transcript)

            template = analyze(utterance.chat)

            print(template)

            if isinstance(template, dict):

                if template["utterance_type"] == UtteranceType.QUESTION:
                    brain_response = app.brain.query_brain(template)
                    reply = utils.reply_to_question(brain_response, [])
                else:
                    brain_response = app.brain.update(template)
                    reply = phrasing.phrase_update(brain_response)

                print(reply)

                if isinstance(reply, str) or isinstance(reply, unicode):

                    # Return Score and Response
                    # Make sure to not execute the response here, but just to return the response function
                    return 1.0, lambda: app.say(re.sub(r"[\s+_]", " ", reply))
        except Exception as e:
            pass
            # print("NLP/Brain Error: {}: {}".format(type(e), e))
