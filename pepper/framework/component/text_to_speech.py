from pepper.framework.abstract import AbstractComponent
from pepper.framework.util import Scheduler
from threading import Lock

from typing import Optional, Union


class TextToSpeechComponent(AbstractComponent):
    """
    Text To Speech Component. Exposes the say() Method to Applications

    Parameters
    ----------
    backend: AbstractBackend
        Application Backend
    """

    def __init__(self, backend):
        super(TextToSpeechComponent, self).__init__(backend)

        # Prevent Racing Conditions
        self._microphone_lock = Lock()

        def worker():
            # type: () -> None
            """Make sure Microphone is not listening when Text to Speech is Live"""

            # Acquire Microphone Lock
            with self._microphone_lock:
                # If robot is not talking & microphone is not yet running -> Start Microphone
                if not self.backend.text_to_speech.talking and not self.backend.microphone.running:
                    self.backend.microphone.start()

        schedule = Scheduler(worker, name="TextToSpeechComponentThread")
        schedule.start()

    def say(self, text, animation=None, block=False):
        # type: (Union[str, unicode], Optional[str], bool) -> None
        """
        Say Text (with optional Animation) through Text-to-Speech

        Parameters
        ----------
        text: str
            Text to say through Text-to-Speech
        animation: str or None
            (Naoqi) Animation to play
        block: bool
            Whether this function should block or immediately return after calling
        """

        # Acquire Microphone Lock
        with self._microphone_lock:

            # Stop Microphone if running
            if self.backend.microphone.running:
                self.backend.microphone.stop()

            # Say Text through Text-to-Speech
            self.backend.text_to_speech.say(text, animation, block)
