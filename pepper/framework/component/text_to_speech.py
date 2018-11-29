from pepper.framework.abstract import AbstractComponent
from pepper.framework.util import Scheduler
from threading import Lock


class TextToSpeechComponent(AbstractComponent):
    def __init__(self, backend):
        super(TextToSpeechComponent, self).__init__(backend)

        self._microphone_lock = Lock()

        def worker():
            with self._microphone_lock:
                # If talking is over & microphone is not yet running -> Start Microphone
                if not self.backend.text_to_speech.talking and not self.backend.microphone.running:
                    self.backend.microphone.start()

        schedule = Scheduler(worker, name="TextToSpeechComponentThread")
        schedule.start()

    def say(self, text, animation=None):
        """
        Say Text (with Animation) through Text-to-Speech

        Parameters
        ----------
        text: str
            Text to say through Text-to-Speech
        animation: str or None
            (Naoqi) Animation to play
        """

        # Acquire Microphone Lock
        with self._microphone_lock:
            # Stop Microphone if running
            if self.backend.microphone.running:
                self.backend.microphone.stop()

            # Say Text through Text-to-Speech
            self.backend.text_to_speech.say(text, animation)
