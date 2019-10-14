from pepper.framework.abstract import AbstractImage
from pepper.framework.sensor.obj import Object
from pepper.framework.util import Bounds
from pepper import logger, config

from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score
import numpy as np

from time import sleep
import subprocess
import socket
import os

from typing import Dict


class Face(Object):
    """
    Face Object

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
    image: AbstractImage
        Image Face was Found in
    """

    UNKNOWN = config.HUMAN_UNKNOWN

    def __init__(self, name, confidence, representation, bounds, image):
        # type: (str, float, np.ndarray, Bounds, AbstractImage) -> None
        super(Face, self).__init__(config.HUMAN_UNKNOWN if name == FaceClassifier.NEW else name,
                                   confidence, bounds, image)

        self._representation = representation

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


class OpenFace(object):
    """
    Perform Face Recognition Using OpenFace

    This requires a Docker Image of ```bamos/openface``` and Docker Running, see `The Installation Guide <https://github.com/cltl/pepper/wiki/Installation#3-openface--docker>`_

    If not yet running, this class will:
        1. run the bamos/openface container
        2. copy /util/_openface.py to it
        3. run the server included within the container

    It will then connect a client to this server to request face representations via a socket connection.
    """

    DOCKER_NAME = "openface"
    DOCKER_IMAGE = "bamos/openface"
    DOCKER_WORKING_DIRECTORY = "/root/openface"

    SCRIPT_NAME = '_openface.py'
    SCRIPT_PATH = os.path.join(os.path.dirname(__file__), 'util', SCRIPT_NAME)

    FEATURE_DIM = 128

    HOST, PORT = '127.0.0.1', 8989

    def __init__(self):

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


# TODO: class is not in use, improve it and use it?
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
    """
    Classify Faces of People

    Parameters
    ----------
    people: Dict[str, np.ndarray]
        Known People as <name, representations> dictionary
    n_neighbors: int
    """

    NEW = "NEW"

    def __init__(self, people, n_neighbors=20):
        # type: (Dict[str, np.ndarray], int) -> None

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
        # type: () -> Dict[str, np.ndarray]
        """
        People Dictionary

        Returns
        -------
        people: dict
        """
        return self._people

    def add(self, name, vector):
        # type: (str, np.ndarray) -> None
        """
        Add Person to Face Classifier

        Parameters
        ----------
        name: str
        vector: np.ndarray
            Concatenated Representations (float32 array of length 128n)
        """
        people = self._people
        people[name] = vector

        self._names = sorted(self.people.keys())
        self._indices = range(len(self._names))

        if self.people:
            self._labels = np.concatenate([[index] * len(self.people[name]) for name, index in zip(self._names, self._indices)])
            self._features = np.concatenate([self.people[name] for name in self._names])
            self._classifier = KNeighborsClassifier(self._n_neighbors)
            self._classifier.fit(self._features, self._labels)

    def classify(self, representation, bounds, image):
        """
        Classify Face Observation as Particular Person

        Parameters
        ----------
        representation: np.ndarray
            Observed Face Representation (from OpenFace.represent)
        bounds: Bounds
            Face Bounds (relative to Image)
        image: AbstractImage
            Image in which Face was Observed

        Returns
        -------
        person: Face
            Classified Person
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
        Load People from directory of <name>.bin files

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
