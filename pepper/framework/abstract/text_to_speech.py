from pepper.util import Scheduler
from pepper import logger
from Queue import Queue
from time import sleep

from typing import Optional, Union


class AbstractTextToSpeech(object):
    """
    Abstract Text To Speech

    Parameters
    ----------
    language: str
        Language Code, See: https://cloud.google.com/speech/docs/languages
    """

    def __init__(self, language):
        self._language = language

        self._queue = Queue()
        self._talking_jobs = 0

        self._scheduler = Scheduler(self._worker, name="TextToSpeechThread")
        self._scheduler.start()

        self._log = logger.getChild(self.__class__.__name__)

    @property
    def language(self):
        """
        Language Code, See: https://cloud.google.com/speech/docs/languages

        Returns
        -------
        language: str
            Language Code, See: https://cloud.google.com/speech/docs/languages
        """
        return self._language

    @property
    def talking(self):
        """
        Returns whether system is currently producing speech

        Returns
        -------
        talking: bool
            Whether system is currently producing speech
        """
        return self._talking_jobs >= 1

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
        # self._log.info(text.replace('\n', ' '))
        self._talking_jobs += 1
        self._queue.put((text, animation))

        while block and self.talking:
            sleep(1E-3)

    def on_text_to_speech(self, text, animation=None):
        """
        Say something through Text to Speech (Implementation)

        Text To Speech Modules should implement this function
        This function should block while speech is being produced

        Parameters
        ----------
        text: str
        animation: str
        """
        pass

    def _worker(self):
        self.on_text_to_speech(*self._queue.get())
        self._talking_jobs -= 1
