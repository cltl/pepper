from pepper.framework.abstract import AbstractCamera, AbstractMicrophone, AbstractTextToSpeech
from pepper.framework.asr import AbstractASR
from pepper.framework.vad import VAD
from pepper.framework.face import FaceClassifier
from pepper.framework.object import CocoClassifyClient
from pepper import config

from time import sleep
import logging


class AbstractApp(object):
    def __init__(self, camera, openface, microphone, asr, text_to_speech):
        """
        Initialize Application

        Parameters
        ----------
        camera: AbstractCamera
        microphone: AbstractMicrophone
        asr: AbstractASR
        text_to_speech: AbstractTextToSpeech
        """

        self._camera = camera
        self._camera.callbacks += [self.on_image]

        self._openface = openface
        self._faces = FaceClassifier.load_directory(config.FACE_DIRECTORY)
        self._face_classifier = FaceClassifier(self._faces)

        self._coco = CocoClassifyClient()

        self._microphone = microphone
        self._microphone.callbacks += [self.on_audio]

        self._text_to_speech = text_to_speech

        self._vad = VAD(microphone, [self.on_utterance])
        self._asr = asr

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
    def vad(self):
        return self._vad

    @property
    def asr(self):
        return self._asr

    @property
    def openface(self):
        return self._openface

    @property
    def log(self):
        """
        Returns
        -------
        logger: logging.Logger
        """
        return self._log

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

    def on_image(self, image):
        classes, scores, boxes = self._coco.classify(image)
        self.on_object(image, classes, scores, boxes)

        representation = self.openface.represent(image)
        if representation:
            bounds, face = representation
            self.on_face(bounds, face)

    def on_object(self, image, classes, scores, boxes):
        pass

    def on_face(self, bounds, face):
        name, confidence, distance = self._face_classifier.classify(face)

        if distance > config.FACE_RECOGNITION_NEW_DISTANCE_THRESHOLD:
            self.on_face_new(bounds, face)
        if confidence > config.FACE_RECOGNITION_KNOWN_CONFIDENCE_THRESHOLD:
            self.on_face_known(bounds, face, name)

    def on_face_known(self, bounds, face, name):
        pass

    def on_face_new(self, bounds, face):
        pass

    def on_audio(self, audio):
        pass

    def on_utterance(self, audio):
        hypotheses = self.asr.transcribe(audio)
        if hypotheses:
            self.on_transcript(hypotheses)

    def on_transcript(self, transcript):
        pass
