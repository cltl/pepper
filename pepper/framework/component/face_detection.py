from pepper.framework.abstract import AbstractComponent
from pepper.framework.sensor.face import OpenFace, FaceClassifier, Face
from pepper.framework.util import Scheduler
from pepper import config

from Queue import Queue
from typing import List, NoReturn


class FaceDetectionComponent(AbstractComponent):
    """
    Perform Face Detection using :class:`~pepper.sensor.face.OpenFace` and :class:`~pepper.sensor.face.FaceClassifier`
    on every :class:`~pepper.framework.abstract.camera.AbstractCamera` on_image event.
    """

    def __init__(self, backend):
        """
        Construct Face Detection Component

        Parameters
        ----------
        backend: AbstractBackend
        """
        super(FaceDetectionComponent, self).__init__(backend)

        self.on_face_callbacks = []
        self.on_person_callbacks = []
        self.on_new_person_callbacks = []

        # Initialize OpenFace
        open_face = OpenFace()

        # Import Face Data
        people = FaceClassifier.load_directory(config.PEOPLE_FRIENDS_ROOT)
        people.update(FaceClassifier.load_directory(config.PEOPLE_NEW_ROOT))

        # Initialize Face Classifier
        self.face_classifier = FaceClassifier(people)

        queue = Queue()

        def on_image(image):
            """
            Raw On Image Event. Called every time the camera yields a frame.

            Parameters
            ----------
            image: np.ndarray
            """
            queue.put([self.face_classifier.classify(r, b, image) for r, b in open_face.represent(image)])

        def worker():
            on_face = queue.get()

            on_face_known = []
            on_face_new = []

            for face in on_face:
                if face.confidence > config.FACE_RECOGNITION_THRESHOLD:
                    (on_face_new if face.name == FaceClassifier.NEW else on_face_known).append(face)

            if on_face: self.on_face(on_face)
            if on_face_known: self.on_face_known(on_face_known)
            if on_face_new: self.on_face_new(on_face_new)

        # Initialize Queue & Worker
        schedule = Scheduler(worker, name="FaceDetectionComponentThread")
        schedule.start()

        # Add on_image to Camera Callbacks
        self.backend.camera.callbacks += [on_image]

    def on_face(self, faces):
        # type: (List[Face]) -> None
        pass

    def on_face_known(self, faces):
        # type: (List[Face]) -> None
        pass

    def on_face_new(self, faces):
        # type: (List[Face]) -> None
        pass
