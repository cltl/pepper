from pepper.framework.abstract import AbstractApp
from pepper.sensor import FaceClassifier, CocoClassifyClient, VAD
from pepper.brain import LongTermMemory
from pepper import config

import logging
from time import sleep


class BaseApp(AbstractApp):
    def __init__(self, openface, asr, camera, microphone, text_to_speech):
        """
        Initialize Base Application -> Base for all Applications and BDI

        The base application takes platform specific inputs as parameters and sets up new callbacks,
        this allows keeping the same application structure over a range of hardware (Pepper/Nao/PC for now)

        # TODO: Solve Weird Error when Loading OpenFace after loading SystemMicrophone

        Parameters
        ----------
        intention: AbstractIntention
        camera: pepper.framework.abstract.AbstractCamera
        openface: pepper.framework.OpenFace
        microphone: pepper.framework.AbstractMicrophone
        asr: pepper.sensor.asr.AbstractASR
        text_to_speech: pepper.framework.abstract.AbstractTextToSpeech
        """
        super(BaseApp, self).__init__()

        # Set Intention
        self._intention = self
        self._intention.app = self

        # Add Camera
        self._camera = camera
        self._camera.callbacks += [self._on_image]

        # Add Microphone
        self._microphone = microphone
        self._microphone.callbacks += [self.on_audio]

        # Add OpenFace and FaceClassifier
        self._openface = openface
        self._faces = FaceClassifier.load_directory(config.FACE_DIRECTORY)
        self._face_classifier = FaceClassifier(self._faces)

        # Add Coco Client
        self._coco = CocoClassifyClient()

        # Add Text to Speech
        self._text_to_speech = text_to_speech

        # Add Voice Activity Detection and Automatic Speech Recognition
        self._vad = VAD(microphone, [self._on_utterance])
        self._asr = asr

        self._brain = LongTermMemory()

        # Get Logger
        self._log = logging.getLogger(self.__class__.__name__)
        self._log.debug("Booted")

        self._running = False

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
        value: pepper.framework.AbstractIntention
        """

        self.log.info("{} -> {}".format(self._intention.__class__.__name__, value.__class__.__name__))
        self._intention = value

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
        camera: pepper.framework.AbstractCamera
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
        text_to_speech: pepper.framework.AbstractTextToSpeech
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
    def faces(self):
        return self._faces

    @property
    def brain(self):
        """
        Returns
        -------
        brain: LongTermMemory
        """
        return self._brain

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
        objects: list of tuple
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

    def on_transcript(self, transcript, audio):
        """
        On Transcript Event. Called every time an utterance was understood by Automatic Speech Recognition.

        Parameters
        ----------
        transcript: list of (str, float)
            Hypotheses (text, confidence) about the corresponding utterance
        """
        self.intention.on_transcript(transcript, audio)

    def _on_image(self, image):
        """
        Raw On Image Event. Called every time the camera yields a frame.

        Parameters
        ----------
        image: np.ndarray
        """

        # Call On Image Event
        self.on_image(image)

        # Classify Objects in Frame, calling On Object if any are found
        classes, scores, boxes = self._coco.classify(image)
        objects = [(cls['name'], scr, box)
                   for cls, scr, box in zip(classes, scores, boxes) if scr > config.OBJECT_CONFIDENCE_THRESHOLD]
        if objects: self.on_object(image, objects)

        # Represent Faces and call appropriate events when they are known or new
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

        # Call On Utterance Event
        self.on_utterance(audio)

        # If Transcript, call On Transcript Event
        hypotheses = self.asr.transcribe(audio)
        if hypotheses:
            self.on_transcript(hypotheses, audio)


