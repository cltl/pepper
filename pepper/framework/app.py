from pepper.framework.abstract import AbstractApp
from pepper.framework.abstract import AbstractIntention
from pepper.sensor import FaceClassifier, CocoClassifyClient, CocoObject, VAD

from pepper.brain import LongTermMemory

from pepper.web.server import VideoFeedApplication
from pepper.util.image import ImageAnnotator
from pepper.util.image import ImageWriter

from pepper import config

from PIL import Image
import numpy as np

from threading import Thread
from Queue import Queue
from time import sleep
import logging


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
        self._intention = AbstractIntention(self)
        self._intention.app = self

        # Add Camera
        self._camera = camera
        self._camera.callbacks += [self._on_image]

        # Object Queue & Worker
        self._object_queue = Queue()
        self._object_thread = Thread(target=self._on_object_worker)
        self._object_thread.daemon = True
        self._object_thread.start()

        # Face Queue & Worker
        self._face_queue = Queue()
        self._face_thread = Thread(target=self._on_face_worker)
        self._face_thread.daemon = True
        self._face_thread.start()

        # Add Microphone
        self._microphone = microphone
        self._microphone.callbacks += [self.on_audio]

        # Add OpenFace and FaceClassifier
        self._openface = openface
        self._faces = FaceClassifier.load_directory(config.FACE_DIRECTORY)
        self._faces.update(FaceClassifier.load_directory(config.NEW_FACE_DIRECTORY))
        self._face_classifier = FaceClassifier(self._faces)

        # Add Coco Client
        self._coco = CocoClassifyClient()

        # Add Text to Speech
        self._text_to_speech = text_to_speech

        # Add Voice Activity Detection and Automatic Speech Recognition
        self._vad = VAD(microphone, [self._on_utterance])
        self._asr = asr

        # Initialize Brain
        self._brain = LongTermMemory()

        # Add-ons
        if config.REALTIME_STATISTICS:
            self._statistics_thread = Thread(target=self._statistics)
            self._statistics_thread.daemon = True
            self._statistics_thread.start()

        if config.SAVE_VIDEO_FEED:
            self._image_writer = ImageWriter()
            self.camera.callbacks.append(self._image_writer.write)

        if config.SHOW_VIDEO_FEED:
            self._video_feed_application = VideoFeedApplication()

            self._image_annotator = ImageAnnotator()

            self._video_feed_application_thread = Thread(target=self._video_feed_application.start)
            self._video_feed_application_thread.daemon = True
            self._video_feed_application_thread.start()

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

    def say(self, text):
        self.microphone.stop()
        self.text_to_speech.say(text)
        self.microphone.start()

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
        objects: list of CocoObject
            List of CocoObject instances
        """
        self.intention.on_object(image, objects)

    def on_face(self, faces):
        """
        On Face Event. Called every time a face is detected.

        Parameters
        ----------
        faces: list of pepper.sensor.face.Face
            Face Object
        """
        self.intention.on_face(faces)

    def on_face_known(self, persons):
        """
        On Face Known Event. Called every time a known face is detected.

        Parameters
        ----------
        persons: list of pepper.sensor.face.Person
        """
        self.intention.on_face_known(persons)

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

    def on_transcript(self, hypotheses, audio):
        """
        On Transcript Event. Called every time an utterance was understood by Automatic Speech Recognition.

        Parameters
        ----------
        hypotheses: List[ASRHypothesis]
            Hypotheses about the corresponding utterance
        """
        self.intention.on_transcript(hypotheses, audio)

    def _on_utterance(self, audio):

        # Call On Utterance Event
        self.on_utterance(audio)

        # If Transcript, call On Transcript Event
        hypotheses = self.asr.transcribe(audio)
        if hypotheses:
            self.on_transcript(hypotheses, audio)

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
        objects = [obj for obj in self._coco.classify(image) if obj.confidence > config.OBJECT_CONFIDENCE_THRESHOLD]

        # Represent Faces and call appropriate events when they are known or new
        persons = [self._face_classifier.classify(face) for face in self.openface.represent(image)]
        persons = [person for person in persons if person.confidence > config.FACE_RECOGNITION_THRESHOLD]

        self._object_queue.put((image, objects))
        self._face_queue.put(persons)

        if config.SHOW_VIDEO_FEED:
            image = Image.fromarray(image)
            image = self._image_annotator.annotate(image, objects, persons)
            self._video_feed_application.update(image)

    def _on_object_worker(self):
        while True:
            image, objects = self._object_queue.get()
            if objects: self.on_object(image, objects)

    def _on_face_worker(self):
        while True:
            persons = self._face_queue.get()
            if persons: self.on_face_known(persons)

    def _statistics(self):
        while True:

            activation_bars = int(self.vad.activation * 10)

            print "\rMicrophone {:3.1f} kHz | Camera {:4.1f} Hz | Voice {:12s} {:4s}".format(
                self._microphone._true_rate / 1000, self._camera._true_rate,
                ("<{:10s}>" if self.vad._voice else "[{:10s}]").format("|" * activation_bars + "." * (10 - activation_bars)) if self.microphone._running else "[          ]",
                "{:4.0%}".format(self.vad.activation) if self.microphone._running else "   %"
            ),
            sleep(0.1)


