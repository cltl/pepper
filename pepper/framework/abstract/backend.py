from . import AbstractCamera, AbstractMicrophone, AbstractTextToSpeech


class AbstractBackend(object):
    def __init__(self, camera, microphone, text_to_speech):
        """
        Backend Template

        Parameters
        ----------
        camera: AbstractCamera
        microphone: AbstractMicrophone
        text_to_speech: AbstractTextToSpeech
        """
        self._camera = camera
        self._microphone = microphone
        self._text_to_speech = text_to_speech

    @property
    def camera(self):
        """
        Returns
        -------
        camera: AbstractCamera
        """
        return self._camera

    @property
    def microphone(self):
        """
        Returns
        -------
        microphone: AbstractMicrophone
        """
        return self._microphone

    @property
    def text_to_speech(self):
        """
        Returns
        -------
        text_to_speech: AbstractTextToSpeech
        """
        return self._text_to_speech
