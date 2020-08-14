from pepper.framework.abstract import AbstractBackend, BackendContainer
from pepper.framework.event.api import EventBusContainer
from pepper import logger

from logging import Logger
from typing import ClassVar


class ComponentDependencyError(Exception):
    """Raised when a Component Dependency hasn't been met"""
    pass

# TODO For now use the mixin pattern, unify dependency management
class AbstractComponent(BackendContainer, EventBusContainer):
    """
    Abstract Base Component on which all Components are Based

    Parameters
    ----------
    backend: AbstractBackend
        Application :class:`~pepper.framework.abstract.backend.AbstractBackend`
    """

    def __init__(self):
        # type: () -> None
        super(AbstractComponent, self).__init__()

        self._log = logger.getChild(self.__class__.__name__)

    @property
    def log(self):
        # type: () -> Logger
        """
        Returns Component `Logger <https://docs.python.org/2/library/logging.html>`_

        Returns
        -------
        logger: logging.Logger
        """
        return self._log

    def require(self, cls, dependency):
        # type: (ClassVar[AbstractComponent], ClassVar[AbstractComponent]) -> AbstractComponent
        """
        Enforce Component Dependency by throwing an Exception when a dependency is missing

        Checks whether Dependency Component is present in the Method Resolution Order (mro)

        Parameters
        ----------
        cls: type
            Dependent: Component Type requiring dependency
        dependency: type
            Dependency: Component Type being dependency

        Returns
        -------
        dependency: AbstractComponent
            Requested Dependency
        """
        if not isinstance(self, dependency):
            raise ComponentDependencyError("{} depends on {}, which is not a superclass of {}".format(
                cls.__name__, dependency.__name__, self.__class__.__name__))

        if self.__class__.mro().index(cls) > self.__class__.mro().index(dependency):
            raise ComponentDependencyError("{0} depends on {1}, but {1} is not initialized before {0} in {2}".format(
                cls.__name__, dependency.__name__, self.__class__.__name__))

        return self
