from pepper.framework.abstract import AbstractComponent
from pepper.sensor.face import OpenFace, FaceClassifier
from pepper import config

from Queue import Queue
from threading import Thread


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

        face_queue = Queue()
        person_queue = Queue()

        def on_image(image):
            """
            Raw On Image Event. Called every time the camera yields a frame.

            Parameters
            ----------
            image: np.ndarray
            """

            # Find Persons
            faces = open_face.represent(image)
            persons = [self.face_classifier.classify(face) for face in faces]
            persons = [person for person in persons if person.confidence > config.FACE_RECOGNITION_THRESHOLD]

            face_queue.put(faces)
            person_queue.put(persons)

        def worker():
            while True:
                faces = face_queue.get()
                if faces:

                    # Call on_face Event Function
                    self.on_face(faces)

                    # Call Callbacks
                    for callback in self.on_face_callbacks:
                        callback(faces)

                persons = person_queue.get()
                if persons:

                    if persons[0].name == FaceClassifier.NEW:
                        self.on_new_person(persons)
                        for callback in self.on_new_person_callbacks:
                            callback(persons)
                    else:
                        # Call on_person Event Function
                        self.on_person(persons)

                        # Call Callback Functions
                        for callback in self.on_person_callbacks:
                            callback(persons)

        # Initialize Queue & Worker
        thread = Thread(target=worker)
        thread.daemon = True
        thread.start()

        # Add on_image to Camera Callbacks
        self.backend.camera.callbacks += [on_image]

    def on_face(self, faces):
        """
        On Face Event. Called every time a face is detected.

        Parameters
        ----------
        faces: list of pepper.sensor.face.Face
            Face Object
        """
        pass

    def on_person(self, persons):
        """
        On Person Event. Called every time a known face is detected.

        Parameters
        ----------
        persons: list of pepper.sensor.face.Person
        """
        pass

    def on_new_person(self, persons):
        """
        On New Person Event. Called every time an unknown face is detected.

        Parameters
        ----------
        persons: list of pepper.sensor.face.Person
        """
        pass


