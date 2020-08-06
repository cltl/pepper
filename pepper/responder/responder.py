from time import time

from enum import Enum
from typing import List, Union, Tuple, Optional, ClassVar, Callable

from pepper import logger
from pepper.framework.abstract import AbstractComponent, AbstractApplication
from pepper.language import Utterance


class ResponderRequirementUnmetError(Exception):
    pass


class ResponderType(Enum):
    Intention = 9
    Topic = 8
    Sensory = 7
    Personal = 6
    Brain = 5
    Conversational = 4
    Internet = 3
    PAID = 2
    Unknown = 1


RESPONDER_TYPES = sorted(ResponderType, key=lambda item: item.value, reverse=True)


class Responder(object):
    @property
    def type(self):
        # type: () -> ResponderType
        raise NotImplementedError()

    @property
    def requirements(self):
        # type: () -> List[ClassVar[AbstractComponent]]
        """
        Lists Component Requirement for this Responder Object

        Returns
        -------
        requirements: list of AbstractComponent
            List of required Components
        """
        raise NotImplementedError()

    def respond(self, utterance, app):
        # type: (Utterance, Union[requirements]) -> Optional[Tuple[float, Callable]]
        """
        Respond to Utterance

        When successful, respond should return a quality score and a callable implementing the response

        Parameters
        ----------
        utterance: Utterance
            Utterance to respond to
        app: Union[requirements]
            Components to Interact with as Response

        Returns
        -------
        response: float, callable
            response quality & responder function
        """
        raise NotImplementedError()


class ResponsePicker(object):

    def __init__(self, app, responders):
        # type: (AbstractApplication, List[Responder]) -> None

        self._app = app

        self._responders = responders

        self._groups = [[r for r in responders if r.type == t] for t in RESPONDER_TYPES]

        self._log = logger.getChild(self.__class__.__name__)

        self._check_requirements()

    @property
    def responders(self):
        # type: () -> List[Responder]
        return self._responders

    @property
    def groups(self):
        return self._groups

    @property
    def app(self):
        # type: () -> AbstractApplication
        return self._app

    def respond(self, utterance):
        # type: (Utterance) -> Optional[Responder]

        for group in self.groups:

            t0 = time()

            best_score = 0
            best_responder = None  # type: Responder
            best_func = None  # type: Callable[[], None]

            for responder in group:

                result = responder.respond(utterance, self.app)

                if result:
                    score, func = result

                    if score > best_score:
                        best_responder = responder
                        best_score = score
                        best_func = func

                    if best_responder and best_func:

                        self._log.info("{} ({:3.2f}s)".format(best_responder.__class__.__name__, time() - t0))

                        best_func()
                        return best_responder

    def _check_requirements(self):
        unmet_requirements = set()

        for responder in self.responders:
            for requirement in responder.requirements:
                if not isinstance(self.app, requirement):
                    unmet_requirements.add(requirement)

        if unmet_requirements:
            raise ResponderRequirementUnmetError("{} depends on {}, but these are not superclasses of {}".format(
                self.__class__.__name__, unmet_requirements, self.app.__class__.__name__))