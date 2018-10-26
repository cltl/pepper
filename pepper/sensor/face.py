from pepper.sensor.obj import Bounds
from pepper import logger

from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score
import numpy as np

from time import sleep
import subprocess
import socket
import os


class Face(object):
    def __init__(self, representation, bounds):
        """
        OpenFace Face Information

        Parameters
        ----------
        representation: np.ndarray
            Face Feature Vector
        bounds: Bounds
            Face Bounding Box
        """
        self._representation = representation
        self._bounds = bounds

    @property
    def representation(self):
        """
        Returns
        -------
        representation: np.ndarray
            Face Feature Vector
        """
        return self._representation

    @property
    def bounds(self):
        """
        Returns
        -------
        bounds: Bounds
            Face Bounding Box
        """
        return self._bounds


class Person(Face):
    def __init__(self, face, name, confidence):
        """
        Parameters
        ----------
        face: Face
            OpenFace Face
        name: str
            Name of Person
        confidence: float
            Name Confidence
        """
        super(Person, self).__init__(face.representation, face.bounds)

        self._name = name
        self._confidence = confidence

    @property
    def name(self):
        """
        Returns
        -------
        name: str
            Name of Person
        """
        return self._name

    @property
    def confidence(self):
        """
        Returns
        -------
        confidence: float
            Name Confidence
        """
        return self._confidence

    def __repr__(self):
        return "{}[{:3.0%}]: '{}'".format(self.__class__.__name__, self.confidence, self.name)


class OpenFace(object):
    DOCKER_IMAGE = "bamos/openface"
    DOCKER_WORKING_DIRECTORY = "/root/openface"
    DOCKER_NAME = "openface"

    SCRIPT_NAME = '_openface.py'
    SCRIPT_PATH = os.path.join(os.path.dirname(__file__), 'util', SCRIPT_NAME)

    FEATURE_DIM = 128

    HOST, PORT = '127.0.0.1', 8989

    def __init__(self):
        """Run OpenFace Client (& Server, if it is not yet running)"""

        self._log = logger.getChild(self.__class__.__name__)

        if not self._openface_running():

            self._log.debug("{} is not running -> booting it!".format(OpenFace.DOCKER_IMAGE))

            # Start OpenFace image and run server on it
            subprocess.call(['docker', 'run',                                           # Run Docker Image
                             '-d',                                                      # Detached Mode (Non-Blocking)
                             '-w', self.DOCKER_WORKING_DIRECTORY,                       # Working Directory
                             '-p', '{}:{}:{}'.format(self.HOST, self.PORT, self.PORT),  # Port Forwarding
                             '--rm',                                                    # Remove on Stop
                             '--name', self.DOCKER_NAME,                                # Name for Docker Image
                             self.DOCKER_IMAGE])                                        # Docker Image to Run

            # Copy and Execute OpenFace Script in Docker
            subprocess.call(['docker', 'cp', self.SCRIPT_PATH, "{}:/root/openface".format(self.DOCKER_NAME)])
            subprocess.call(['docker', 'exec', '-d', self.DOCKER_NAME, 'python', "./{}".format(self.SCRIPT_NAME)])
            sleep(5)  # Wait for Server to Boot (I know this is not elegant)

        self._log.debug("Booted")

    def represent(self, image):
        """
        Represent Face in Image as 128-dimensional vector

        Parameters
        ----------
        image: np.ndarray
            Image (possibly containing a human face)

        Returns
        -------
        result: list of Face
            List of Face objects
        """

        try:
            # Connect to OpenFace Service
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.HOST, self.PORT))

            # Send Image
            client.send(np.array(image.shape, np.int32))
            client.sendall(image.tobytes())

            # Receive Number of Faces in Image
            n_faces = np.frombuffer(client.recv(4), np.int32)[0]

            # Wrap information into Face instances
            faces = []
            for i in range(n_faces):
                bounds = Bounds(*np.frombuffer(client.recv(4*4), np.float32)).scaled(1.0 / image.shape[1], 1.0 / image.shape[0])
                representation = np.frombuffer(client.recv(self.FEATURE_DIM * 4), np.float32)
                faces.append(Face(representation, bounds))
            return faces

        except socket.error as e:
            raise RuntimeError("Couldn't connect to OpenFace Docker service.")

    def stop(self):
        """Stop OpenFace Image"""
        subprocess.call(['docker', 'stop', self.DOCKER_NAME])

    def _openface_running(self):
        """
        Check if OpenFace service is currently running

        Returns
        -------
        is_running: bool
        """
        try:
            return 'openface' in subprocess.check_output(['docker', 'ps'])
        except Exception as e:
            return False


class FaceClassifier:

    NEW = "NEW"

    def __init__(self, people, n_neighbors=20):
        """
        Classify Faces of Known People

        Parameters
        ----------
        people: dict
        new: dict
        n_neighbors: int
        """

        self._people = people
        self._n_neighbors = n_neighbors

        self._names = sorted(self.people.keys())
        self._indices = range(len(self._names))

        if self.people:
            self._labels = np.concatenate([[index] * len(self.people[name]) for name, index in zip(self._names, self._indices)])
            self._features = np.concatenate([self.people[name] for name in self._names])
            self._classifier = KNeighborsClassifier(self._n_neighbors)
            self._classifier.fit(self._features, self._labels)

        self._log = logger.getChild(self.__class__.__name__)
        self._log.debug("Booted")

    @property
    def people(self):
        """
        Returns
        -------
        people: dict
        """
        return self._people

    def classify(self, face):
        """
        Classify Face as Person

        Parameters
        ----------
        face: Face

        Returns
        -------
        person: Person
        """

        if not self.people:
            return Person(face, "human", 0.0)

        # Get distances to nearest Neighbours
        distances, indices = self._classifier.kneighbors(face.representation.reshape(-1, OpenFace.FEATURE_DIM))
        distances, indices = distances[0], indices[0]

        # Get numerical label associated with closest face
        labels = self._labels[indices]
        label = np.bincount(labels).argmax()

        # Retrieve name and calculate confidence
        name = self._names[label]
        confidence = float(np.mean(labels == label))

        return Person(face, name, confidence)

    def accuracy(self):
        """
        Calculate Classifier Cross Validation Accuracy

        Returns
        -------
        accuracy: float
        """
        return float(np.mean(cross_val_score(self._classifier, self._features, self._labels, cv=5)))

    @classmethod
    def from_directory(cls, directory):
        """
        Construct FaceClassifier from directory of <name>.bin files

        Parameters
        ----------
        directory: str

        Returns
        -------
        face_classifier: FaceClassifier
        """
        return cls(FaceClassifier.load_directory(directory))

    @staticmethod
    def load_directory(directory):
        """
        Load Directory of <name>.bin files

        Parameters
        ----------
        directory: str

        Returns
        -------
        people: dict
            Dictionary of <name>: <representations> pairs
        """
        people = {}
        for path in os.listdir(directory):
            name = os.path.splitext(path)[0]
            features = np.fromfile(os.path.join(directory, path), np.float32).reshape(-1, OpenFace.FEATURE_DIM)
            people[name] = features
        return people
