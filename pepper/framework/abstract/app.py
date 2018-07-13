from pepper.framework.abstract import AbstractCamera, AbstractMicrophone, AbstractTextToSpeech
from pepper.framework.vad import VAD

from time import sleep
import logging


class AbstractApp(object):
    def __init__(self, camera, microphone, text_to_speech):
        self._camera = camera
        self._microphone = microphone
        self._text_to_speech = text_to_speech
        self._vad = VAD(microphone, [self.on_utterance])

        self._running = False

        self._log = logging.getLogger(self.__class__.__name__)
        self._log.debug("Booted")

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

    @property
    def log(self):
        """
        Returns
        -------
        logger: logging.Logger
        """
        return self._log

    def on_image(self, image):
        pass

    def on_audio(self, audio):
        pass

    def on_utterance(self, audio):
        pass

    def start(self):
        self.run()

    def stop(self):
        self.camera.stop()
        self.microphone.stop()
        self._running = False

    def run(self):
        self.camera.start()
        self.microphone.start()
        self._running = True
        while self._running:
            sleep(1)