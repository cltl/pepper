from pepper.framework import FaceClassifier, CocoClassifyClient, VAD
from pepper import config

import numpy as np

from time import sleep
import logging


class AbstractApp(object):
    @property
    def camera(self):
        """
        Returns
        -------
        camera: AbstractCamera
        """
        raise NotImplementedError()

    @property
    def microphone(self):
        """
        Returns
        -------
        microphone: pepper.framework.abstract.AbstractMicrophone
        """
        raise NotImplementedError()

    @property
    def text_to_speech(self):
        """
        Returns
        -------
        text_to_speech: AbstractTextToSpeech
        """
        raise NotImplementedError()

    @property
    def vad(self):
        """
        Returns
        -------
        vad: VAD
        """
        raise NotImplementedError()

    @property
    def asr(self):
        """
        Returns
        -------
        asr: pepper.framework.AbstractASR
        """
        raise NotImplementedError()

    @property
    def openface(self):
        """
        Returns
        -------
        openface: pepper.framework.OpenFace
        """
        raise NotImplementedError()

    @property
    def log(self):
        """
        Returns
        -------
        logger: logging.Logger
        """
        raise NotImplementedError()

    def start(self):
        """Start Application"""
        raise NotImplementedError()

    def stop(self):
        """Stop Application"""
        raise NotImplementedError()

    def run(self):
        """Run Application"""
        raise NotImplementedError()

    def on_image(self, image):
        """
        On Image Event. Called every time the camera captures a frame

        Parameters
        ----------
        image: np.ndarray
            Camera Frame
        """
        pass

    def on_object(self, image, objects):
        """
        On Object Event. Called every time one or more objects are detected in a camera frame.

        Parameters
        ----------
        image: np.ndarray
            Camera Frame
        objects: list of (str, float, list of float)
            List of Objects: [(name, confidence score, bounding box)]
        """
        pass

    def on_face(self, bounds, face):
        """
        On Face Event. Called every time a face is detected.

        Parameters
        ----------
        bounds: list of float
            Bounding Box for Face
        face: np.ndarray
            128-dimensional OpenFace representation of Face
        """
        pass

    def on_face_known(self, bounds, face, name):
        """
        On Face Known Event. Called every time a known face is detected.

        Parameters
        ----------
        bounds: list of float
            Bounding Box for Face
        face: np.ndarray
            128-dimensional OpenFace representation of Face
        name: str
            Name associated with Face
        """
        pass

    def on_face_new(self, bounds, face):
        """
        On Face New Event. Called every time a new face is detected.

        Parameters
        ----------
        bounds: list of float
            Bounding Box for Face
        face: np.ndarray
            128-dimensional OpenFace representation of Face
        """
        pass

    def on_audio(self, audio):
        """
        On Audio Event. Called for every microphone sample window.

        Parameters
        ----------
        audio: np.ndarray
            Microphone Samples
        """
        pass

    def on_utterance(self, audio):
        """
        On Utterance Event. Called every time an utterance was detected.

        Parameters
        ----------
        audio: np.ndarray
            Microphone Samples containing speech
        """
        pass

    def on_transcript(self, transcript):
        """
        On Transcript Event. Called every time an utterance was understood by Automatic Speech Recognition.

        Parameters
        ----------
        transcript: list of (float, str)
            Hypotheses (confidence, text) about the corresponding utterance
        """
        pass


class BaseApp(AbstractApp):
    def __init__(self, camera, openface, microphone, asr, text_to_speech):
        """
        Initialize Abstract Application -> Base for all Applications and BDI

        The base application takes platform specific inputs as parameters and sets up event callbacks,
        this allows keeping the same application structure over a range of hardware (Pepper/Nao/PC for now)

        # TODO: Solve Weird Error when Loading OpenFace after loading SystemMicrophone

        Parameters
        ----------
        camera: pepper.framework.abstract.AbstractCamera
        openface: pepper.framework.OpenFace
        microphone: pepper.framework.AbstractMicrophone
        asr: pepper.framework.AbstractASR
        text_to_speech: pepper.framework.abstract.AbstractTextToSpeech
        """
        super(BaseApp, self).__init__()


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
        """
        On Image Event. Called every time the camera captures a frame

        Parameters
        ----------
        image: np.ndarray
            Camera Frame
        """
        pass

    def on_object(self, image, objects):
        """
        On Object Event. Called every time one or more objects are detected in a camera frame.

        Parameters
        ----------
        image: np.ndarray
            Camera Frame
        objects: list of (str, float, list of float)
            List of Objects: [(name, confidence score, bounding box)]
        """
        pass

    def on_face(self, bounds, face):
        """
        On Face Event. Called every time a face is detected.

        Parameters
        ----------
        bounds: list of float
            Bounding Box for Face
        face: np.ndarray
            128-dimensional OpenFace representation of Face
        """
        pass

    def on_face_known(self, bounds, face, name):
        """
        On Face Known Event. Called every time a known face is detected.

        Parameters
        ----------
        bounds: list of float
            Bounding Box for Face
        face: np.ndarray
            128-dimensional OpenFace representation of Face
        name: str
            Name associated with Face
        """
        pass

    def on_face_new(self, bounds, face):
        """
        On Face New Event. Called every time a new face is detected.

        Parameters
        ----------
        bounds: list of float
            Bounding Box for Face
        face: np.ndarray
            128-dimensional OpenFace representation of Face
        """
        pass

    def on_audio(self, audio):
        """
        On Audio Event. Called for every microphone sample window.

        Parameters
        ----------
        audio: np.ndarray
            Microphone Samples
        """
        pass

    def on_utterance(self, audio):
        """
        On Utterance Event. Called every time an utterance was detected.

        Parameters
        ----------
        audio: np.ndarray
            Microphone Samples containing speech
        """
        pass

    def on_transcript(self, transcript):
        """
        On Transcript Event. Called every time an utterance was understood by Automatic Speech Recognition.

        Parameters
        ----------
        transcript: list of (float, str)
            Hypotheses (confidence, text) about the corresponding utterance
        """
        pass

    def _on_image(self, image):
        self.on_image(image)

        classes, scores, boxes = self._coco.classify(image)
        objects = [(cls['name'], scr, box)
                   for cls, scr, box in zip(classes, scores, boxes) if scr > config.OBJECT_CONFIDENCE_THRESHOLD]
        if objects: self.on_object(image, objects)

        representation = self.openface.represent(image)
        if representation:
            bounds, face = representation

            name, confidence, distance = self._face_classifier.classify(face)
            self.on_face(bounds, face)

            if distance > config.FACE_RECOGNITION_NEW_DISTANCE_THRESHOLD:
                self.on_face_new(bounds, face)
            elif confidence > config.FACE_RECOGNITION_KNOWN_CONFIDENCE_THRESHOLD:
                self.on_face_known(bounds, face, name)

    def _on_utterance(self, audio):
        self.on_utterance(audio)
        hypotheses = self.asr.transcribe(audio)
        if hypotheses:
            self.on_transcript(hypotheses)

