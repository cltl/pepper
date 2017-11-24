from pepper.vision.classification.data import load_lfw, load_faces
from pepper.event import Event

import numpy as np

from threading import Thread
from time import time, sleep
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

    OUTER_MEAN = 1.7038624
    OUTER_STD = 0.46672297

    INNER_MEAN = 0.22572114728781423
    INNER_STD = 0.091139727503611295

    BACKLOG = 20

    MATCH_THRESHOLD = INNER_MEAN
    NEW_FACE_THRESHOLD = INNER_MEAN + INNER_STD

    def __init__(self, session, on_face, on_new_face, camera, names, representations):
        super(FaceRecognitionEvent, self).__init__(session, on_face)

        self._on_new_face = on_new_face
        self._camera = camera
        self._names = names
        self._representations = representations

        self._recognition = FaceRecognition()

        self._backlog = np.zeros((self.BACKLOG, 128), np.float32)
        self._distance = np.zeros(self.BACKLOG, np.float32)

        self._running = True
        Thread(target=self.run).start()

    @property
    def camera(self):
        return self._camera

    @property
    def names(self):
        return self._names

    @property
    def representations(self):
        return self._representations

    def add_face(self, name, representation):
        self._names.append(name)
        self._representations = np.concatenate((self._representations, representation[None, :]))

    def run(self):
        backlog_index = 0

        while self._running:

            image = self.camera.get()
            face = self._recognition.representation(image)

            if face:
                bounds, representation = face

                outer = FaceRecognition.distance(self.representations, representation)
                outer_min_index = np.argmin(outer)

                self._backlog[backlog_index] = representation
                self._distance[backlog_index] = outer[outer_min_index]

                if outer[outer_min_index] < self.MATCH_THRESHOLD:
                    self.on_face(outer[outer_min_index], self.names[outer_min_index])

                elif np.all(self._distance) and np.min(self._distance) > self.NEW_FACE_THRESHOLD:
                    self._on_new_face(np.mean(self._backlog, 0))
                    self._backlog = np.zeros(self._backlog.shape)
                    self._distance = np.zeros(self._distance.shape)

                backlog_index = (backlog_index + 1) % self.BACKLOG

    def on_face(self, distance, name):
        self.callback(distance, name)

    def on_new_face(self, representation):
        self._on_new_face(representation)

    def close(self):
        self._running = False
        self._recognition.close()


if __name__ == "__main__":
    from pepper.vision.camera import SystemCamera

    face = FaceRecognition()

    N = 5
    representation_matrix = np.empty((N, 128))

    for i in range(N):
        image = SystemCamera().get()

        t = time()
        bounds, representation = face.representation(image)
        print("Image[{}] {:4.4f}".format(i, time() - t))

        representation_matrix[i] = representation


    representation = np.mean(representation_matrix, 0)
    print("Inner Distance {}".format(face.inner_distance(representation_matrix)))
    print("LFW Distance {}".format(face.lfw_distance(representation)[:10]))

    names, matrix = load_faces()
    print("DB Distance {}".format(face.names_distance(names, matrix, representation)))

    face.stop()