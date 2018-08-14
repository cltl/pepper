from pepper.sensor import VAD

import numpy as np

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
        objects: list of tuple
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

    def on_transcript(self, transcript, audio):
        """
        On Transcript Event. Called every time an utterance was understood by Automatic Speech Recognition.

        Parameters
        ----------
        transcript: list of (str, float)
            Hypotheses (confidence, text) about the corresponding utterance
        audio: np.ndarray
            Microphone Samples containing speech
        """
        pass


class AbstractIntention(AbstractApp):
    def __init__(self, app):
        """Create Abstract Intention"""

        self._app = app
        self._log = logging.getLogger(self.__class__.__name__)

    @property
    def app(self):
        """
        Returns
        -------
        app: pepper.framework.BaseApp
        """
        return self._app

    @app.setter
    def app(self, value):
        """
        Parameters
        ----------
        value: BaseApp
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
        text_to_speech: pepper.framework.AbstractTextToSpeech
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
