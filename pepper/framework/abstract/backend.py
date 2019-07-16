from . import AbstractCamera, AbstractMicrophone, AbstractTextToSpeech, AbstractMotion, AbstractLed


class AbstractBackend(object):
    """
    Abstract Backend on which all Backends are based

    Exposes
    :class:`~pepper.framework.abstract.camera.AbstractCamera`,
    :class:`~pepper.framework.abstract.microphone.AbstractMicrophone`,
    :class:`~pepper.framework.abstract.text_to_speech.AbstractTextToSpeech` and
    :class:`~pepper.framework.abstract.led.AbstractLed`.

    Parameters
    ----------
    camera: AbstractCamera
        Backend :class:`~pepper.framework.abstract.camera.AbstractCamera`
    microphone: AbstractMicrophone
        Backend :class:`~pepper.framework.abstract.microphone.AbstractMicrophone`
    text_to_speech: AbstractTextToSpeech
        Backend :class:`~pepper.framework.abstract.text_to_speech.AbstractTextToSpeech`
    led: AbstractLed
        Backend :class:`~pepper.framework.abstract.led.AbstractLed`
    """

    def __init__(self, camera, microphone, text_to_speech, motion, led):
        self._camera = camera
        self._microphone = microphone
        self._text_to_speech = text_to_speech
        self._motion = motion
        self._led = led

    @property
    def camera(self):
        # type: () -> AbstractCamera
        """
        Reference to :class:`~pepper.framework.abstract.camera.AbstractCamera`

        Returns
        -------
        camera: AbstractCamera
        """
        return self._camera

    @property
    def microphone(self):
        # type: () -> AbstractMicrophone
        """
        Reference to :class:`~pepper.framework.abstract.microphone.AbstractMicrophone`

        Returns
        -------
        microphone: AbstractMicrophone
        """
        return self._microphone

    @property
    def text_to_speech(self):
        # type: () -> AbstractTextToSpeech
        """
        Reference to :class:`~pepper.framework.abstract.text_to_speech.AbstractTextToSpeech`

        Returns
        -------
        text_to_speech: AbstractTextToSpeech
        """
        return self._text_to_speech

    @property
    def motion(self):
        # type: () -> AbstractMotion
        """
        Reference to :class:`~pepper.framework.abstract.motion.AbstractMotion`

        Returns
        -------
        motion: AbstractMotion
        """
        return self._motion

    @property
    def led(self):
        # type: () -> AbstractLed
        """
        Reference to :class:`~pepper.framework.abstract.led.AbstractLed`

        Returns
        -------
        text_to_speech: AbstractLed
        """
        return self._led
