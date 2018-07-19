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
        transcript: list of (str, float)
            Hypotheses (confidence, text) about the corresponding utterance
        """
        pass


class AbstractIntention(AbstractApp):
    def __init__(self):
        """
        Create Abstract Intention

        Parameters
        ----------
        app: AbstractApp
        """

        self._app = None
        self._log = logging.getLogger(self.__class__.__name__)

    @property
    def app(self):
        """
        Returns
        -------
        app: AbstractApp
        """
        return self._app

    @app.setter
    def app(self, value):
        """
        Parameters
        ----------
        value: AbstractApp
        """
        self._app = value

    @property
    def log(self):
        """
        Returns
        -------
        logger: logging.Logger
        """
        return self._log

    @property
    def camera(self):
        """
        Returns
        -------
        camera: AbstractCamera
        """
        return self.app.camera

    @property
    def microphone(self):
        """
        Returns
        -------
        microphone: pepper.framework.abstract.AbstractMicrophone
        """
        return self.app.microphone

    @property
    def text_to_speech(self):
        """
        Returns
        -------
        text_to_speech: AbstractTextToSpeech
        """
        return self.app.text_to_speech

    @property
    def vad(self):
        """
        Returns
        -------
        vad: VAD
        """
        return self.app.vad

    @property
    def asr(self):
        """
        Returns
        -------
        asr: pepper.framework.AbstractASR
        """
        return self.app.asr

    @property
    def openface(self):
        """
        Returns
        -------
        openface: pepper.framework.OpenFace
        """
        return self.app.openface


class BaseApp(AbstractApp):
    def __init__(self, intention, camera, openface, microphone, asr, text_to_speech):
        """
        Initialize Base Application -> Base for all Applications and BDI

        The base application takes platform specific inputs as parameters and sets up event callbacks,
        this allows keeping the same application structure over a range of hardware (Pepper/Nao/PC for now)

        # TODO: Solve Weird Error when Loading OpenFace after loading SystemMicrophone

        Parameters
        ----------
        intention: AbstractIntention
        camera: pepper.framework.abstract.AbstractCamera
        openface: pepper.framework.OpenFace
        microphone: pepper.framework.AbstractMicrophone
        asr: pepper.framework.AbstractASR
        text_to_speech: pepper.framework.abstract.AbstractTextToSpeech
        """
        super(BaseApp, self).__init__()

        self._intention = intention
        self._intention.app = self

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
    def intention(self):
        """
        Returns
        -------
        intention: AbstractIntention
        """
        return self._intention

    @intention.setter
    def intention(self, value):
        """
        Parameters
        ----------
        value: AbstractIntention
        """
        self._intention = value
        self._intention.app = self

    @property
    def log(self):
        """
        Returns
        -------
        logger: logging.Logger
        """
        return self._log

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
        self.intention.on_image(image)

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
        self.intention.on_object(image, objects)

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
        self.intention.on_face(bounds, face)

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
        self.intention.on_face_known(bounds, face, name)

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
        self.intention.on_face_new(bounds, face)

    def on_audio(self, audio):
        """
        On Audio Event. Called for every microphone sample window.

        Parameters
        ----------
        audio: np.ndarray
            Microphone Samples
        """
        self.intention.on_audio(audio)

    def on_utterance(self, audio):
        """
        On Utterance Event. Called every time an utterance was detected.

        Parameters
        ----------
        audio: np.ndarray
            Microphone Samples containing speech
        """
        self.intention.on_utterance(audio)

    def on_transcript(self, transcript):
        """
        On Transcript Event. Called every time an utterance was understood by Automatic Speech Recognition.

        Parameters
        ----------
        transcript: list of (str, float)
            Hypotheses (text, confidence) about the corresponding utterance
        """
        self.intention.on_transcript(transcript)

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
