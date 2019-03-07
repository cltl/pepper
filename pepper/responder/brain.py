from pepper.framework import *
from pepper.language import Utterance
from .responder import Responder, ResponderType
from pepper.knowledge import animations

from pepper.language import analyze

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

        # TODO: See whether we can form a response from 'utterance'

        able_to_respond = False

        if able_to_respond:

            # TODO: Implement Actual Response
            def response():

                # Access Brain
                print(app.brain)

                # Access Text to Speech
                app.say(text="I have something sensible to say!", animation=animations.COGITATE)

            # Return Score and Response
            # Make sure to not execute the response here, but just to return the response function
            return 1.0, response
