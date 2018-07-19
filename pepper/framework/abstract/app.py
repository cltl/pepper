from pepper.framework import FaceClassifier, CocoClassifyClient, VAD
from pepper import config

import numpy as np

from time import sleep
import logging


class AbstractApp(object):
    def __init__(self, camera, openface, microphone, asr, text_to_speech):
        """
        Initialize Abstract Application -> Base for all Applications and BDI

        The base application takes platform specific inputs as parameters and sets up event callbacks,
        this allows keeping the same application structure over a range of hardware (Pepper/Nao/PC for now)

        # TODO: Rename AbstractApp, since it is not really abstract
        # TODO: Solve Weird Error when Loading OpenFace after loading SystemMicrophone

        Parameters
        ----------
        camera: pepper.framework.abstract.AbstractCamera
        openface: pepper.framework.OpenFace
        microphone: pepper.framework.AbstractMicrophone
        asr: pepper.framework.AbstractASR
        text_to_speech: pepper.framework.abstract.AbstractTextToSpeech
        """
        super(AbstractApp, self).__init__()


        self._camera = camera
        self._camera.callbacks += [self._on_image]

        self._openface = openface
        self._faces = FaceClassifier.load_directory(config.FACE_DIRECTORY)
        self._face_classifier = FaceClassifier(self._faces)

        self._coco = CocoClassifyClient()

        self._microphone = microphone
        self._microphone.callbacks += [self.on_audio]

        self._text_to_speech = text_to_speech

        self._vad = VAD(microphone, [self._on_utterance])
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
        microphone: pepper.framework.abstract.AbstractMicrophone
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
        """
        Returns
        -------
        vad: VAD
        """
        return self._vad

    @property
    def asr(self):
        """
        Returns
        -------
        asr: pepper.framework.AbstractASR
        """
        return self._asr

    @property
    def openface(self):
        """
        Returns
        -------
        openface: pepper.framework.OpenFace
        """
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
        """Start Application"""

        self.run()

    def stop(self):
        """Stop Application"""

        self.camera.stop()
        self.microphone.stop()
        self._running = False

    def run(self):
        """Run Application"""

        self.camera.start()
        self.microphone.start()
        self._running = True

        while self._running:
            sleep(1)

    def on_image(self, image):
        pass

    def on_object(self, image, objects):
        pass

    def on_face(self, bounds, face):
        pass

    def on_face_known(self, bounds, face, name):
        pass

    def on_face_new(self, bounds, face):
        pass

    def on_audio(self, audio):
        pass

    def on_utterance(self, audio):
        pass

    def on_transcript(self, transcript):
        pass

    def _on_image(self, image):
        self.on_image(image)

        classes, scores, boxes = self._coco.classify(image)
        objects = [(cls['name'], scr, (np.array(box).reshape(2,2).T * self.camera.shape[:2]).astype(np.uint32))
                   for cls, scr, box in zip(classes, scores, boxes) if scr > config.OBJECT_CONFIDENCE_THRESHOLD]
        if objects: self.on_object(image, objects)

        representation = self.openface.represent(image)
        if representation:
            bounds, face = representation

            name, confidence, distance = self._face_classifier.classify(face)

            if distance > config.FACE_RECOGNITION_NEW_DISTANCE_THRESHOLD:
                self.on_face_new(bounds, face)
            elif confidence > config.FACE_RECOGNITION_KNOWN_CONFIDENCE_THRESHOLD:
                self.on_face_known(bounds, face, name)
            else: self.on_face(bounds, face)

    def _on_utterance(self, audio):
        self.on_utterance(audio)
        hypotheses = self.asr.transcribe(audio)
        if hypotheses:
            self.on_transcript(hypotheses)

