from pepper import logger

class AbstractTextToSpeech(object):
    def __init__(self, language):
        """
        Parameters
        ----------
        language: str
            Language Code, See: https://cloud.google.com/speech/docs/languages
        """

        self._language = language
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

    def say(self, text):
        """
        Say something through Text to Speech

        Parameters
        ----------
        text: str
        """
        raise NotImplementedError()