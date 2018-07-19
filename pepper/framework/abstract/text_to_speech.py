class AbstractTextToSpeech(object):
    def __init__(self):
        """Abstract Text to Speech"""
        pass

    def say(self, text):
        """
        Say something through Text to Speech

        Parameters
        ----------
        text: str
        """
        raise NotImplementedError()