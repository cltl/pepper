from pepper.framework.abstract import AbstractBackend, AbstractComponent
from pepper.brain import LongTermMemory
from pepper import logger

from time import sleep


class IntentionDependencyError(Exception): pass


class Application(AbstractComponent):

    EVENT_TAG = 'on_'

    def __init__(self, backend):
        """
        Create Application

        Parameters
        ----------
        backend: AbstractBackend
        """
        super(Application, self).__init__(backend)

        self._brain = LongTermMemory()

        self._events = {attr: self.__getattribute__(attr) for attr in dir(self)
                        if attr.startswith(self.EVENT_TAG) and callable(self.__getattribute__(attr))}

        self._log = logger.getChild(self.__class__.__name__)
        self.log.debug("Booted")

    @property
    def log(self):
        """
        Returns
        -------
        log: logging.Logger
        """
        return self._log

    @property
    def dependencies(self):
        for cls in self.__class__.mro():
            if issubclass(cls, AbstractComponent) and not cls == AbstractComponent and \
                    not issubclass(cls, Application) and not issubclass(cls, Intention):
                yield cls

    @property
    def brain(self):
        """
        Returns
        -------
        brain: LongTermMemory
        """
        return self._brain

    def say(self, text):
        self.backend.microphone.stop()
        self.backend.text_to_speech.say(text)
        self.backend.microphone.start()

    def run(self):
        self.backend.camera.start()
        self.backend.microphone.start()

        while True:
            sleep(1)

    def _reset_events(self):
        for event_name, event_function in self._events.items():
            self.__setattr__(event_name, event_function)


class Intention(object):
    def __init__(self, application):
        """
        Parameters
        ----------
        application: Application
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
        Returns
        -------
        log: logging.Logger
        """
        return self._log

    @property
    def application(self):
        return self._application

    @property
    def dependencies(self):
        for cls in self.__class__.mro():
            if issubclass(cls, AbstractComponent) and not cls == AbstractComponent and \
                    not issubclass(cls, Application) and not issubclass(cls, Intention):
                yield cls

    def say(self, text):
        self.application.say(text)

    def require_dependency(self, dependency):
        """
        Require Component Dependency

        Parameters
        ----------
        dependency: type

        Returns
        -------
        dependency: AbstractComponent
        """
        if not isinstance(self.application, dependency):
            raise IntentionDependencyError("{} depends on {}, which is not included in {}".format(
                self.__class__.__name__, dependency.__name__, self.application.__class__.__name__))

        for attribute in dir(dependency):
            if attribute.startswith(Application.EVENT_TAG):
                self._application.__setattr__(attribute, self.__getattribute__(attribute))

        return self.application
