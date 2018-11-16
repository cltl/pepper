from pepper.framework.abstract import AbstractBackend, AbstractComponent
from pepper.framework.abstract.component import ComponentDependencyError
from pepper.brain import LongTermMemory
from pepper import logger

from time import sleep
from threading import Lock


class Application(AbstractComponent):
    """
    The Application class is at the base of every robot application.
    It keeps track of events from different Components
    and allows for Intentions to be build in top of it.
    """

    _EVENT_TAG = 'on_'

    def __init__(self, backend):
        """
        Create Application from Backend

        Parameters
        ----------
        backend: AbstractBackend
        """
        super(Application, self).__init__(backend)

        self._brain = LongTermMemory()

        self._events = {attr: self.__getattribute__(attr) for attr in dir(self)
                        if attr.startswith(self._EVENT_TAG) and callable(self.__getattribute__(attr))}

        self._mutex = Lock()

        self._log = logger.getChild(self.__class__.__name__)
        self.log.debug("Booted")

    @property
    def log(self):
        """
        Application Logger

        Returns
        -------
        log: logging.Logger
        """
        return self._log

    @property
    def dependencies(self):
        """
        Application Dependencies

        Yields
        ------
        components: iterable of AbstractComponent
        """
        for cls in self.__class__.mro():
            if issubclass(cls, AbstractComponent) and not cls == AbstractComponent and \
                    not issubclass(cls, Application) and not issubclass(cls, Intention):
                yield cls

    @property
    def brain(self):
        """
        Brain associated with Application

        Returns
        -------
        brain: LongTermMemory
        """

        # TODO: Make Brain into Component
        return self._brain

    def say(self, text, animation=None):
        """
        Say Text (with Animation) through Text-to-Speech

        Parameters
        ----------
        text: str
            Text to Say through Text-to-Speech
        animation: str or None
            (Naoqi) Animation to Play
        """
        with self._mutex:
            if self.backend.microphone.running:
                self.backend.microphone.stop()
            self.backend.text_to_speech.say(text, animation)

    def run(self):
        """
        Run Application

        Starts Camera & Microphone and sleeps Main Thread
        """
        self.backend.camera.start()
        self.backend.microphone.start()

        while True:
            with self._mutex:
                if not self.backend.text_to_speech.talking and not self.backend.microphone.running:
                    self.backend.microphone.start()
            sleep(0.01)

    def _reset_events(self):
        """Reset Events Callbacks to their (unimplemented) Defaults"""
        for event_name, event_function in self._events.items():
            self.__setattr__(event_name, event_function)


class Intention(object):
    """
    The Intention class is at the base of more involved robot applications.
    They build on top of applications an allow for switching of robot contexts.
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

        self._log = logger.getChild(self.__class__.__name__)
        self.log.info("<- Switched Intention")

    @property
    def log(self):
        """
        Intention Loggeer

        Returns
        -------
        log: logging.Logger
        """
        return self._log

    @property
    def application(self):
        """
        Application Intention is based on

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

    def say(self, text, animation=None):
        """
        Say Text (with Animation) through Text-to-Speech

        Parameters
        ----------
        text: str
            Text to Say through Text-to-Speech
        animation: str or None
            (Naoqi) Animation to Play
        """
        self.application.say(text, animation)

    def require_dependency(self, dependency):
        """
        Require Component Dependency

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
