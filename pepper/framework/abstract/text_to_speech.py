from pepper import logger

from threading import Thread
from Queue import Queue


class AbstractTextToSpeech(object):
    def __init__(self, language):
        """
        Parameters
        ----------
        language: str
            Language Code, See: https://cloud.google.com/speech/docs/languages
        """

        self._language = language

        self._queue = Queue()
        self._talking_jobs = 0

        self._thread = Thread(name="TextToSpeechThread", target=self._worker)
        self._thread.daemon = True
        self._thread.start()

        self._log = logger.getChild(self.__class__.__name__)

    @property
    def language(self):
        """
        Returns
        -------
        language: str
            Language Code, See: https://cloud.google.com/speech/docs/languages
        """
        return self._language

    @property
    def talking(self):
        """
        Returns
        -------
        talking: bool
            Whether system is currently producing speech
        """
        return self._talking_jobs >= 1

    def say(self, text, animation=None):
        """
        Say something through Text to Speech (Interface)

        Parameters
        ----------
        text: str
        animation: str
        """
        self._log.info(text)
        self._talking_jobs += 1
        self._queue.put((text, animation))

    def on_text_to_speech(self, text, animation=None):
        """
        Say something through Text to Speech (Implementation)

        Parameters
        ----------
        text: str
        animation: str
        """
        pass

    def _worker(self):
        while True:
            self.on_text_to_speech(*self._queue.get())
            self._talking_jobs -= 1
