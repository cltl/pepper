from pepper.framework.abstract import AbstractComponent
from threading import Thread, Lock
from time import sleep


class TextToSpeechComponent(AbstractComponent):
    def __init__(self, backend):
        super(TextToSpeechComponent, self).__init__(backend)

        self._microphone_lock = Lock()

        def worker():
            while True:
                with self._microphone_lock:
                    # If talking is over & microphone is not yet running -> Start Microphone
                    if not self.backend.text_to_speech.talking and not self.backend.microphone.running:
                        self.backend.microphone.start()
                        sleep(1E-3)

        thread = Thread(name="TextToSpeechComponentThread", target=worker)
        thread.daemon = True
        thread.start()

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
