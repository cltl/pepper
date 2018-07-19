from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score
import numpy as np

from time import sleep
import subprocess
import socket
import os

import logging


def docker_openface_running():
    try:
        return 'openface' in subprocess.check_output(['docker', 'ps'])
    except Exception as e:
        return False


class FaceBounds:
    def __init__(self, x, y, width, height):
        self._x = x
        self._y = y
        self._width = width
        self._height = height

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def center(self):
        return self.x + self.width / 2, self.y + self.height / 2

    @property
    def area(self):
        return self.width * self.height

    def __str__(self):
        return "FaceBounds({:1.2f},{:1.2f},{:1.2f},{:1.2f}): {:1.2f}".format(
            self.x, self.y, self.width, self.height, self.area)


class OpenFace(object):
    DOCKER_IMAGE = "bamos/openface"
    DOCKER_WORKING_DIRECTORY = "/root/openface"
    DOCKER_NAME = "openface"

    SCRIPT_NAME = '_openface.py'
    SCRIPT_PATH = os.path.join(os.path.dirname(__file__), 'util', SCRIPT_NAME)

    HOST, PORT = '127.0.0.1', 8989

    def __init__(self):

        self._log = logging.getLogger(self.__class__.__name__)

        if not docker_openface_running():

            self._log.debug("{} is not running -> booting it!".format(OpenFace.DOCKER_IMAGE))

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
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.HOST, self.PORT))

        client.send(np.array(image.shape, np.int32))
        client.sendall(image.tobytes())

        success = np.frombuffer(client.recv(4), np.int32)[0]

        if success:
            bounds = FaceBounds(*np.frombuffer(client.recv(4*4), np.float32))
            representation_length = np.frombuffer(client.recv(4), np.int32)[0]
            representation = np.frombuffer(client.recv(representation_length * 4), np.float32)
            return bounds, representation

    def stop(self):
        subprocess.call(['docker', 'stop', self.DOCKER_NAME])


class FaceClassifier:

    FEATURE_DIM = 128

    def __init__(self, people, n_neighbors=20):
        self._people = people
        self._names = sorted(people.keys())
        self._indices = range(len(self._names))

        if self.people:
            self._labels = np.concatenate([[index] * len(people[name]) for name, index in zip(self._names, self._indices)])
            self._features = np.concatenate([people[name] for name in self._names])
            self._classifier = KNeighborsClassifier(n_neighbors)
            self._classifier.fit(self._features, self._labels)

    @property
    def people(self):
        return self._people

    def classify(self, face):
        if self.people:
            distances, indices = self._classifier.kneighbors(face.reshape(-1, self.FEATURE_DIM))
            distances, indices = distances[0], indices[0]

            labels = self._labels[indices]
            label = np.bincount(labels).argmax()
            name = self._names[label]
            confidence = np.mean(labels == label)
            distance = np.mean(distances[labels == label])
            return name, confidence, distance
        return "", 0, 0

    def accuracy(self):
        return np.mean(cross_val_score(self._classifier, self._features, self._labels, cv=5))

    @classmethod
    def from_directory(cls, directory):
        return cls(FaceClassifier.load_directory(directory))

    @staticmethod
    def load_directory(directory):
        people = {}
        for path in os.listdir(directory):
            name = os.path.splitext(path)[0]
            features = np.fromfile(os.path.join(directory, path), np.float32).reshape(-1, FaceClassifier.FEATURE_DIM)
            people[name] = features
        return people
