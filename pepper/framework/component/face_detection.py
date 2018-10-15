from pepper.framework.abstract import AbstractComponent
from pepper.sensor.face import OpenFace, FaceClassifier
from pepper import config

from Queue import Queue
from threading import Thread


class FaceDetection(AbstractComponent):
    def __init__(self, backend):
        """
        Construct Face Detection Component

        Parameters
        ----------
        backend: AbstractBackend
        """
        super(FaceDetection, self).__init__(backend)

        self.on_face_callbacks = []
        self.on_person_callbacks = []

        # Initialize OpenFace
        open_face = OpenFace()

        # Import Face Data
        self.known_people = FaceClassifier.load_directory(config.FACE_DIRECTORY)
        self.known_people.update(FaceClassifier.load_directory(config.NEW_FACE_DIRECTORY))

        # Initialize Face Classifier
        face_classifier = FaceClassifier(self.known_people)

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
            persons = [face_classifier.classify(face) for face in faces]
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


