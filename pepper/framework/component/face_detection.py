from pepper.framework.abstract import AbstractImage
from pepper.framework.abstract.component import AbstractComponent
from pepper.framework.sensor.face import FaceClassifier, Face
from pepper.framework.util import Scheduler, Mailbox
from pepper import config

from typing import List
from pepper import logger


class FaceRecognitionComponent(AbstractComponent):
    """
    Perform Face Detection using :class:`~pepper.sensor.face.OpenFace` and :class:`~pepper.sensor.face.FaceClassifier`
    on every :class:`~pepper.framework.abstract.camera.AbstractCamera` on_image event.
    """

    def __init__(self):
        # type: () -> None
        super(FaceRecognitionComponent, self).__init__()

        self._log.info("Initializing FaceRecognitionComponent")

        # Public Lists of Callbacks:
        # Allowing other Components to Subscribe to them
        self.on_face_callbacks = []
        self.on_face_known_callbacks = []
        self.on_face_new_callbacks = []

        face_detector = self.face_detector

        # Import Face Data (Friends & New)
        people = FaceClassifier.load_directory(config.PEOPLE_FRIENDS_ROOT)
        people.update(FaceClassifier.load_directory(config.PEOPLE_NEW_ROOT))

        # Initialize Face Classifier
        self.face_classifier = FaceClassifier(people)

        # Initialize Image Mailbox
        mailbox = Mailbox()

        def on_image(image):
            # type: (AbstractImage) -> None
            """
            Private On Image Event. Called every time the camera yields a frame.

            Parameters
            ----------
            image: AbstractImage
            """
            mailbox.put(image)

        def worker():
            # type: () -> None
            """Find and Classify Faces in Images"""

            # Get latest Image from Mailbox
            image = mailbox.get()

            # Get All Face Representations from OpenFace & Initialize Known/New Face Categories
            on_face = [self.face_classifier.classify(r, b, image) for r, b in face_detector.represent(image.image)]
            on_face_known = []
            on_face_new = []

            # Distribute Faces over Known & New (Keeping them in the general on_face)
            for face in on_face:
                if face.name == config.HUMAN_UNKNOWN:
                    if face.confidence >= 1.0:
                        on_face_new.append(face)
                elif face.confidence > config.FACE_RECOGNITION_THRESHOLD:
                    on_face_known.append(face)

            # Call Appropriate Callbacks
            if on_face:
                for callback in self.on_face_callbacks:
                    callback(on_face)
                self.on_face(on_face)
            if on_face_known:
                for callback in self.on_face_known_callbacks:
                    callback(on_face_known)
                self.on_face_known(on_face_known)
            if on_face_new:
                for callback in self.on_face_new_callbacks:
                    callback(on_face_new)
                self.on_face_new(on_face_new)

        # Initialize Worker
        schedule = Scheduler(worker, name="FaceDetectionComponentThread")
        schedule.start()
        self._log.info("Started FaceDetectionComponent worker")

        # Add on_image to Camera Callbacks
        self.backend.camera.callbacks += [on_image]

        self._log.info("Initialized FaceDetectionComponent")


    def on_face(self, faces):
        # type: (List[Face]) -> None
        """
        On Face Event. Called with all faces in Image

        Parameters
        ----------
        faces: List[Face]
            List of all faces in Image
        """
        pass

    def on_face_known(self, faces):
        # type: (List[Face]) -> None
        """
        On Face Known Event. Called with all known faces in Image

        Parameters
        ----------
        faces: List[Face]
            List of all Known Faces in Image
        """
        pass

    def on_face_new(self, faces):
        # type: (List[Face]) -> None
        """
        On Face New Event. Called with all new faces in Image

        Parameters
        ----------
        faces: List[Face]
            List of all New Faces in Image
        """
        pass
