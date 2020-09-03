import os

import numpy as np
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from typing import Dict

from pepper import logger, config
from pepper.framework.abstract import AbstractImage
from pepper.framework.util import Bounds
from .api import FaceDetector
from .obj import Object


# TODO extract interfaces to .api


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
        super(Face, self).__init__(name, confidence, bounds, image)

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
        faces.update(FaceStore.load_face(os.path.join(directory, path))
                for path in os.listdir(directory) if path.endswith(FaceStore.EXTENSION))
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
        if not path.endswith(FaceStore.EXTENSION):
            raise ValueError("Wrong file extension for " + str(path))
        name = os.path.splitext(os.path.basename(path))[0]
        representation = np.fromfile(path, np.float32).reshape(-1, FaceDetector.FEATURE_DIM)
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


class FaceClassifier(object):
    """
    Classify Faces of People

    Parameters
    ----------
    people: Dict[str, np.ndarray]
        Known People as <name, representations> dictionary
    n_neighbors: int
    """
    EXTENSION = ".bin"

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
        self._log.info("Initialized FaceClassifier")

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
            return Face(Face.UNKNOWN, 0.0, representation, bounds, image)

        # Get distances to nearest Neighbours
        distances, indices = self._classifier.kneighbors(representation.reshape(-1, FaceDetector.FEATURE_DIM))
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
            if path.endswith(FaceClassifier.EXTENSION):
                name = os.path.splitext(path)[0]
                features = np.fromfile(os.path.join(directory, path), np.float32).reshape(-1, FaceDetector.FEATURE_DIM)
                people[name] = features
        return people
