from pepper.vision.classification.data import load_lfw, load_lfw_gender

import numpy as np
from scipy import stats

from time import sleep
import subprocess
import socket
import os


# This Script does Face Detection using OpenFace
# OpenFace is accessed using the 'bamos/openface' Docker image
# Please start Docker and pull the 'bamos/openface' image
# This script will run the image, upload the server script and connect to it!


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


class FaceRecognition:

    DOCKER_IMAGE = "bamos/openface"
    DOCKER_WORKING_DIRECTORY = "/root/openface"
    DOCKER_NAME = "openface"

    HOST = '127.0.0.1'

    REPRESENT_NAME = 'represent.py'
    REPRESENT_PATH = os.path.join(os.path.dirname(__file__), 'openface', REPRESENT_NAME)
    REPRESENT_PORT = 8988

    REPRESENT_ALL_NAME = 'represent_all.py'
    REPRESENT_ALL_PATH = os.path.join(os.path.dirname(__file__), 'openface', REPRESENT_ALL_NAME)
    REPRESENT_ALL_PORT = 8989

    PORT_BIND = '{}:{}:{}'.format(HOST, REPRESENT_ALL_PORT, REPRESENT_ALL_PORT)

    TMP = os.path.join(os.path.dirname(__file__), 'tmp.jpg')

    def __init__(self):
        # Run Docker container
        subprocess.call(['docker', 'run',
                         '-d',
                         '-w', self.DOCKER_WORKING_DIRECTORY,
                         '-p', '{}:{}:{}'.format(self.HOST, self.REPRESENT_PORT, self.REPRESENT_PORT),
                         '-p', '{}:{}:{}'.format(self.HOST, self.REPRESENT_ALL_PORT, self.REPRESENT_ALL_PORT),
                         '--rm',
                         '--name', self.DOCKER_NAME,
                         self.DOCKER_IMAGE])

        # Copy Python Scripts to container
        subprocess.call(['docker', 'cp', self.REPRESENT_PATH, "{}:/root/openface".format(self.DOCKER_NAME)])
        subprocess.call(['docker', 'cp', self.REPRESENT_ALL_PATH, "{}:/root/openface".format(self.DOCKER_NAME)])

        # Call Python Scripts, which will run as servers inside the container
        subprocess.call(['docker', 'exec', '-d', self.DOCKER_NAME, 'python', "./{}".format(self.REPRESENT_NAME)])
        subprocess.call(['docker', 'exec', '-d', self.DOCKER_NAME, 'python', "./{}".format(self.REPRESENT_ALL_NAME)])

        sleep(5)  # Wait for Setup, TODO: Make more elegant..

    @staticmethod
    def distance(matrix, representation):
        return np.sum((matrix - representation) ** 2, 1)

    @staticmethod
    def inner_distance(matrix):
        return np.mean(FaceRecognition.distance(matrix, np.mean(matrix, 0)))

    @staticmethod
    def names_distance(names, matrix, representation):
        distance = FaceRecognition.distance(matrix, representation)
        return [(names[i], distance[i]) for i in np.argsort(distance)]

    @staticmethod
    def lfw_distance(representation):
        names, matrix = load_lfw()
        return FaceRecognition.names_distance(names, matrix, representation)

    @staticmethod
    def gender(representation):
        N = 100

        names, matrix = load_lfw()
        gender = load_lfw_gender()

        distance = FaceRecognition.distance(matrix, representation)
        sorting = np.argsort(distance)
        score = np.average(gender[sorting[:N]], weights=distance[sorting[:N]])

        classification = score > 0.5
        probability = 1 + score * np.log(score + np.finfo(score.dtype).eps)

        return classification, probability

    def representation(self, image):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.HOST, self.REPRESENT_PORT))

        array = np.array(image)
        client.send(np.array(array.shape, np.int32))
        client.sendall(array.tobytes())

        success = np.frombuffer(client.recv(4), np.int32)[0]

        if success:
            bounds = FaceBounds(*np.frombuffer(client.recv(4*4), np.float32))
            representation_length = np.frombuffer(client.recv(4), np.int32)[0]
            representation = np.frombuffer(client.recv(representation_length * 4), np.float32)

            return bounds, representation

    def full_representation(self, image):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.HOST, self.REPRESENT_ALL_PORT))

        array = np.array(image)
        client.send(np.array(array.shape, np.int32))
        client.sendall(array.tobytes())

        number = np.frombuffer(client.recv(4), np.int32)[0]

        if not number: return []

        representations = []
        bounds = []
        areas = []

        for n in range(number):
            bound = FaceBounds(*np.frombuffer(client.recv(4*4), np.float32))
            bounds.append(bound)

            areas.append(bound.area)
            representation_length = np.frombuffer(client.recv(4), np.int32)[0]
            representations.append(np.frombuffer(client.recv(representation_length * 4), np.float32))

        return [(bounds[i], representations[i]) for i in np.argsort(areas)[::-1]]

    def close(self):
        self.stop()

    def stop(self):
        subprocess.call(['docker', 'stop', self.DOCKER_NAME])


class PersonRecognition:

    # Average distance between faces of one person versus
    # Average distance to the face of the closest other person
    INNER_DISTANCE_MEAN, INNER_DISTANCE_STD = 0.49405375, 0.11498976
    OUTER_DISTANCE_MEAN, OUTER_DISTANCE_STD = 0.59587806, 0.17431158

    def __init__(self, names, matrix):
        """
        Person Recognition

        Parameters
        ----------
        names: sized
        matrix: np.ndarray
        """
        self._names = names
        self._matrix = matrix

        print(len(names), len(matrix))

    @property
    def names(self):
        return self._names

    @property
    def matrix(self):
        return self._matrix

    def add(self, name, face):
        self._names.append(name)
        self._matrix = np.concatenate((self._matrix, face.reshape(1, 128)))

    def distance(self, face):
        return np.linalg.norm(self.matrix - face, 2, 1)

    def closest(self, face):
        distance = self.distance(face)
        index = int(np.argmin(distance))
        name = self.names[index]
        return name, distance[index]

    def classify(self, face, threshold_known = 0.8, threshold_new=0.95):
        name, distance = self.closest(face)

        inner_probability = stats.norm.sf(distance, self.INNER_DISTANCE_MEAN, self.INNER_DISTANCE_STD)
        outer_probability = stats.norm.cdf(distance, self.OUTER_DISTANCE_MEAN, self.OUTER_DISTANCE_STD)

        print(name, distance, inner_probability, outer_probability)

        if inner_probability > threshold_known:
            return name
        elif outer_probability > threshold_new:
            return True
        else: return None
