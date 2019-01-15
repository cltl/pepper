from pepper.framework.sensor.obj import Bounds
from pepper import logger

from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score
import numpy as np

from time import sleep
import subprocess
import socket
import os


class Face(object):
    def __init__(self, name, confidence, representation, bounds, image):
        """
        Parameters
        ----------
        name: str
            Name of Person
        confidence: float
            Name Confidence
        representation: np.ndarray
            Face Feature Vector
        bounds: Bounds
            Face Bounding Box
        image: np.ndarray
            Image Face was Found in
        """
        self._image = image
        self._representation = representation
        self._bounds = bounds
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

    @property
    def representation(self):
        """
        Face Representation

        Returns
        -------
        representation: np.ndarray
            Face Feature Vector
        """
        return self._representation

    @property
    def bounds(self):
        """
        Face Bounds (Relative to Image)

        Returns
        -------
        bounds: Bounds
            Face Bounding Box
        """
        return self._bounds

    @property
    def image(self):
        """
        Returns
        -------
        image: np.ndarray
        """
        return self._image

    def __repr__(self):
        return "{}[{:4.0%}]: '{}'".format(self.__class__.__name__, self.confidence, self.name)


class OpenFace(object):
    DOCKER_NAME = "openface"
    DOCKER_IMAGE = "bamos/openface"
    DOCKER_WORKING_DIRECTORY = "/root/openface"

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
        result: list of (np.ndarray, Bounds)
            List of (representation, bounds)
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

                # Face Bounds
                bounds = Bounds(*np.frombuffer(client.recv(4*4), np.float32))
                bounds = bounds.scaled(1.0 / image.shape[1], 1.0 / image.shape[0])

                # Face Representation
                representation = np.frombuffer(client.recv(self.FEATURE_DIM * 4), np.float32)

                faces.append((representation, bounds))

            return faces

        except socket.error:
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
            return self.DOCKER_NAME in subprocess.check_output(['docker', 'ps'])
        except Exception as e:
            return False


class FaceStore(object):

    EXTENSION = ".bin"

    @staticmethod
    def load_directories(*directories):
        faces = {}
        for directory in directories:
            faces.update(FaceStore.load_directory(directory))
        return faces

    @staticmethod
    def load_directory(directory):
        """
        Load all faces from directory with <name>.<FaceStore.EXTENSION> files

        Parameters
        ----------
        directory: str
            Directory containing Face Data

        Returns
        -------
        faces: Dict[str, np.ndarray]
            Dictionary of {name: representation} pairs
        """
        faces = {}
        faces.update(FaceStore.load_face(os.path.join(directory, path)) for path in os.listdir(directory))
        return faces

    @staticmethod
    def load_face(path):
        """
        Load Face in a <name>.<FaceStore.EXTENSION> file

        Parameters
        ----------
        path: str

        Returns
        -------
        name, representation: str, np.ndarray
        """
        name = os.path.splitext(os.path.basename(path))[0]
        representation = np.fromfile(path, np.float32).reshape(-1, OpenFace.FEATURE_DIM)
        return name, representation

    @staticmethod
    def save_face(directory, name, data):
        """
        Save Face to directory in a <name>.<FaceStore.EXTENSION> file

        Parameters
        ----------
        directory: str
            Directory containing Face Data
        name: str
            Name of Person
        data: List[np.ndarray]
            List of Representations: See OpenFace.represent(image) -> Face
        """
        np.concatenate(data).tofile(os.path.join(directory, name + FaceStore.EXTENSION))


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

    def classify(self, representation, bounds, image):
        """
        Classify Face as Person

        Parameters
        ----------
        representation: np.ndarray
        bounds: Bounds
        image: np.ndarray

        Returns
        -------
        person: Face
        """

        if not self.people:
            return Face(self.NEW, 0.0, representation, bounds, image)

        # Get distances to nearest Neighbours
        distances, indices = self._classifier.kneighbors(representation.reshape(-1, OpenFace.FEATURE_DIM))
        distances, indices = distances[0], indices[0]

        # Get numerical label associated with closest face
        labels = self._labels[indices]
        label = np.bincount(labels).argmax()

        # Retrieve name and calculate confidence
        name = self._names[label]
        confidence = float(np.mean(labels == label))

        return Face(name, confidence, representation, bounds, image)

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
