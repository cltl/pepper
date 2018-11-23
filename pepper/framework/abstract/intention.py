from pepper.framework.abstract import AbstractComponent, Application
from pepper.framework.abstract.component import ComponentDependencyError
from pepper import logger


class Intention(object):
    """
    The Intention class is at the base of more involved robot applications.
    They build on top of :class:`~Application` instances an allow for switching of robot contexts.
    """

    def __init__(self, application):
        """
        Parameters
        ----------
        application: Application
            Application to base Intention on
        """
        self._application = application

        # Reset Application Events to their default
        # This prevents events from previous Intention to still be called!
        self.application._reset_events()

        # Subscribe to all Application Events
        for dependency in self.dependencies:
            self.require_dependency(dependency)

        # Subscribe to all Application Members
        self.__dict__.update({k: v for k, v in self.application.__dict__.items() if k not in self.__dict__})

        self._log = logger.getChild(self.__class__.__name__)
        self.log.info("<- Switched Intention")

    @property
    def log(self):
        """
        Intention Logger

        Returns
        -------
        log: logging.Logger
        """
        return self._log

    @property
    def application(self):
        """
        :class:`~Application` Intention is based on

        Returns
        -------
        application: Application
        """
        return self._application

    @property
    def dependencies(self):
        """
        Intention Dependencies

        Yields
        ------
        components: iterable of AbstractComponent
        """
        for cls in self.__class__.mro():
            if issubclass(cls, AbstractComponent) and not cls == AbstractComponent and \
                    not issubclass(cls, Application) and not issubclass(cls, Intention):
                yield cls

    def require_dependency(self, dependency):
        """
        Enforce Component Dependency

        Checks whether Component is included in Application

        Parameters
        ----------
        dependency: type
            Required Component Type

        Returns
        -------
        dependency: AbstractComponent
            Requested Dependency
        """

        if not isinstance(self.application, dependency):
            raise ComponentDependencyError("{} depends on {}, which is not included in {}".format(
                self.__class__.__name__, dependency.__name__, self.application.__class__.__name__))

        for attribute in dir(dependency):
            if attribute.startswith(Application._EVENT_TAG):
                self._application.__setattr__(attribute, self.__getattribute__(attribute))

        return self.application