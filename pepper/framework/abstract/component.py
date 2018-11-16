from pepper.framework.abstract import AbstractBackend
from pepper import logger


class ComponentDependencyError(Exception):
    """Raised when a Component Dependency is not met"""
    pass


class AbstractComponent(object):
    """Abstract Base Component on which all Components are Based"""

    def __init__(self, backend):
        """
        Construct Component

        Parameters
        ----------
        backend: AbstractBackend
            Application Backend
        """
        super(AbstractComponent, self).__init__()

        self._backend = backend
        self._log = logger.getChild(self.__class__.__name__)

    @property
    def log(self):
        """
        Component Logger

        Returns
        -------
        logger: logging.Logger
        """
        return self._log

    @property
    def backend(self):
        """
        Application Backend

        Returns
        -------
        backend: AbstractBackend
        """
        return self._backend

    def require_dependency(self, cls, dependency):
        """
        Specify Component requirement

        Parameters
        ----------
        cls: type
            Component Type requiring dependency
        dependency: type
            Component Type being dependency

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
