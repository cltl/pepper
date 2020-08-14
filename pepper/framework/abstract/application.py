from pepper.framework.abstract import *
from pepper import logger

from logging import Logger
from time import sleep


class AbstractApplication(AbstractComponent):
    """
    The Application class is at the base of every robot application.
    It keeps track of events from different instances of :class:`~pepper.framework.abstract.component.AbstractComponent`,
    allows extension by instances of :class:`~pepper.framework.abstract.intention.AbstractIntention` and
    exposes :class:`~pepper.framework.abstract.backend.AbstractBackend` devices to the Application Layer.
    """

    _EVENT_TAG = 'on_'

    def __init__(self):
        super(AbstractApplication, self).__init__()

        # Find Events associated with Application (inherited from Components)
        self._events = {k: v for k, v in self.__dict__.items() if k.startswith(self._EVENT_TAG) and callable(v)}

        # Instantiate Logger for this Application
        self._log = logger.getChild(self.__class__.__name__)
        self.log.debug("Booted")

    @property
    def log(self):
        # type: () -> Logger
        """
        Returns Application `Logger <https://docs.python.org/2/library/logging.html>`_

        Returns
        -------
        log: logging.Logger
        """
        return self._log

    @property
    def camera(self):
        # type: () -> AbstractCamera
        """
        Returns :class:`~pepper.framework.abstract.camera.AbstractCamera` associated with current Backend

        Returns
        -------
        camera: AbstractCamera
        """
        return self.backend.camera

    @property
    def microphone(self):
        # type: () -> AbstractMicrophone
        """
        Returns :class:`~pepper.framework.abstract.microphone.AbstractMicrophone` associated with current Backend

        Returns
        -------
        microphone: AbstractMicrophone
        """
        return self.backend.microphone

    @property
    def text_to_speech(self):
        # type: () -> AbstractTextToSpeech
        """
        Returns :class:`~pepper.framework.abstract.text_to_speech.AbstractTextToSpeech` associated with current Backend

        Returns
        -------
        text_to_speech: AbstractTextToSpeech
        """
        return self.backend.text_to_speech

    @property
    def motion(self):
        # type: () -> AbstractMotion
        """
        Returns :class:`~pepper.framework.abstract.motion.AbstractMotion` associated with current Backend

        Returns
        -------
        motion: AbstractMotion
        """
        return self.backend.motion

    @property
    def led(self):
        # type: () -> AbstractLed
        """
        Returns :class:`~pepper.framework.abstract.led.AbstractLed` associated with current Backend

        Returns
        -------
        motion: AbstractMotion
        """
        return self.backend.led
    
    @property
    def tablet(self):
        # type: () -> AbstractTablet
        """
        Returns :class:`~pepper.framework.abstract.tablet.AbstractTablet` associated with current Backend

        Returns
        -------
        tablet: AbstractTablet
        """
        return self.backend.tablet

    def run(self):
        """
        Run Application

        Starts Camera & Microphone and Blocks Current Thread until KeyboardInterrupt
        """
        self.backend.camera.start()
        self.backend.microphone.start()

        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            exit(0)

    def _reset_events(self):
        """
        Reset Event Callbacks to their (unimplemented) defaults

        Used when the Application Switches between AbstractIntention, to remove links to the old AbstractIntention
        """
        for event_name, event_function in self._events.items():
            self.__setattr__(event_name, event_function)
