from pepper.framework.abstract import AbstractBackend, AbstractComponent
from pepper import logger

from time import sleep


class Application(AbstractComponent):
    """
    The Application class is at the base of every robot application.
    It keeps track of events from different instances of :class:`~pepper.framework.abstract.component.AbstractComponent`
    and allows for instances of :class:`~Intention` to be build in top of it.
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

        self._events = {attr: self.__getattribute__(attr) for attr in dir(self)
                        if attr.startswith(self._EVENT_TAG) and callable(self.__getattribute__(attr))}

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
        Yields the Dependencies which are fulfilled by this Application

        Yields
        ------
        components: iterable of AbstractComponent
        """
        for cls in self.__class__.mro():
            if issubclass(cls, AbstractComponent) and not cls == AbstractComponent and \
                    not issubclass(cls, Application) and not issubclass(cls, Intention):
                yield cls

    def run(self):
        """
        Run Application

        Starts Camera & Microphone and sleeps Main Thread
        """
        self.backend.camera.start()
        self.backend.microphone.start()

        while True:
            sleep(1)

    def _reset_events(self):
        """Reset Events Callbacks to their (unimplemented) defaults"""
        for event_name, event_function in self._events.items():
            self.__setattr__(event_name, event_function)
