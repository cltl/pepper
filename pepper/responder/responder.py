from pepper.framework import *
from pepper.language import Utterance
from pepper import logger

from enum import IntEnum

from concurrent.futures import ThreadPoolExecutor

from time import time

from typing import List, Union, Tuple, Optional, ClassVar, Callable


class ResponderRequirementUnmetError(Exception):
    pass


class ResponderType(IntEnum):
    Intention = 7
    Sensory = 6
    Brain = 5
    Personal = 4
    Internet = 3
    Conversational = 2
    Unknown = 1


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
    def __init__(self, app, responders, threads=0):
        # type: (AbstractApplication, List[Responder], int) -> None

        self._app = app
        self._responders = responders

        self._threads = ThreadPoolExecutor(threads) if threads else None

        self._log = logger.getChild(self.__class__.__name__)

        self._check_requirements()

    @property
    def responders(self):
        # type: () -> List[Responder]
        return self._responders

    @property
    def app(self):
        # type: () -> AbstractApplication
        return self._app

    def respond(self, utterance):
        # type: (Utterance) -> Responder

        t0 = time()

        all_responders = []

        best_score = 0
        best_responder = None
        best_response = None

        if self._threads:
            futures = [self._threads.submit(responder.respond, utterance, self.app) for responder in self.responders]
            results = [future.result() for future in futures]
        else:
            results = [responder.respond(utterance, self.app) for responder in self.responders]

        for responder, result in zip(self.responders, results):

            if result:
                all_responders.append(responder)

                score, response = result
                score *= responder.type

                if score > best_score:
                    best_score = score
                    best_responder = responder
                    best_response = response

        if best_responder and best_response:

            # Log Results
            self._log.debug("Picked {} from {} in {:3.2f}s".format(
                best_responder.__class__.__name__, [r.__class__.__name__ for r in all_responders], time() - t0))

            # Execute Response
            best_response()

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