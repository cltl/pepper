from pepper.vision.classification.data import load_lfw
from pepper.event import Event

import numpy as np
import subprocess
import socket
import os
from time import time, sleep

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

        sleep(3)  # Wait for Setup, TODO: Make more elegant..

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


class FaceRecognitionEvent(Event):
    def __init__(self, session, callback, names, faces):
        super(FaceRecognitionEvent, self).__init__(session, callback)


if __name__ == "__main__":
    from pepper.vision.camera import SystemCamera

    face = FaceRecognition()

    N = 5
    representation_matrix = np.empty((N, 128))

    for i in range(N):
        image = SystemCamera().get()

        image.show()

        t = time()
        bounds, representation = face.representation(image)
        print("Image[{}] {:4.4f}".format(i, time() - t))

        representation_matrix[i] = representation

    print("Inner Distance {}".format(face.inner_distance(representation_matrix)))
    print("LFW Distance {}".format(face.lfw_distance(np.mean(representation_matrix, 0))[:10]))

    face.stop()