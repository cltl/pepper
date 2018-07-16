class AbstractTextToSpeech(object):
    def __init__(self):
        """Abstract Text to Speech"""
        pass

    def say(self, text):
        """
        Parameters
        ----------
        text: str
        """
        raise NotImplementedError()