"""
The Pepper Responder Package contains logic to determine the correct response to a given Natural Language query.

The :class:`~pepper.responder.responder.ResponsePicker` class decides which
:class:`~pepper.responder.responder.Responder` to pick from a list of potential
:class:`~pepper.responder.responder.Responder`s, based on their :class:`~pepper.responder.responder.ResponderType` and
:meth:`~pepper.responder.responder.Responder.respond` quality.

"""

from .responder import Responder, ResponsePicker, ResponderType
from unknown import UnknownResponder
from .conversational import GreetingResponder, GoodbyeResponder, ThanksResponder, AffirmationResponder, \
    NegationResponder
from .personal import QnAResponder
from .sensory import VisionResponder, PreviousUtteranceResponder, LocationResponder, IdentityResponder, TimeResponder
from .internet import WikipediaResponder, WolframResponder
from .brain import BrainResponder
from .intention import MeetIntentionResponder
from .weather import WeatherResponder, WeatherElserwhere, WeatherMoods