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
    def area(self):
        return self.width * self.height


class Faces:

    DOCKER_IMAGE = "bamos/openface"
    DOCKER_WORKING_DIRECTORY = "/root/openface"
    DOCKER_NAME = "openface"
    PYTHON_SCRIPT_NAME = 'represent.py'
    PYTHON_SCRIPT_PATH = os.path.join(os.path.dirname(__file__), PYTHON_SCRIPT_NAME)
    HOST = '127.0.0.1'
    PORT = 8989
    PORT_BIND = '{}:{}:{}'.format(HOST, PORT, PORT)

    TMP = os.path.join(os.path.dirname(__file__), 'tmp.jpg')

    def __init__(self):
        # Run Docker container
        subprocess.call(['docker', 'run',
                         '-d',
                         '-w', self.DOCKER_WORKING_DIRECTORY,
                         '-p', self.PORT_BIND,
                         '--rm',
                         '--name', self.DOCKER_NAME,
                         self.DOCKER_IMAGE])

        # Copy & Call Python Script
        subprocess.call(['docker', 'cp', self.PYTHON_SCRIPT_PATH, "{}:/root/openface".format(self.DOCKER_NAME)])
        subprocess.call(['docker', 'exec', '-d', self.DOCKER_NAME, 'python', "./{}".format(self.PYTHON_SCRIPT_NAME)])
        sleep(3)

    def lfw_distance(self, image):
        people = self.represent(image)

        if people:
            bounds, representation = people[0]

            LFW_NAMES_PATH = os.path.join(os.path.dirname(__file__), 'data', 'lfw_names.txt')
            LFW_VECTOR_PATH = os.path.join(os.path.dirname(__file__), 'data', 'lfw_vector.bin')

            with open(LFW_NAMES_PATH) as lfw_names_file:
                lfw_names = lfw_names_file.read().split(';')[:-1]

            lfw_vector = np.fromfile(LFW_VECTOR_PATH, np.float32).reshape(len(lfw_names), 128)

            distance = np.sum((representation - lfw_vector) ** 2, 1)

            return [(lfw_names[i], distance[i]) for i in np.argsort(distance)]

    def represent(self, image):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.HOST, self.PORT))

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

    def stop(self):
        subprocess.call(['docker', 'stop', self.DOCKER_NAME])


if __name__ == "__main__":
    from pepper.vision.camera import SystemCamera

    face = Faces()

    image = SystemCamera().get()

    t = time()
    for i, (lfw, distance) in enumerate(face.lfw_distance(image)[:10]):
        print("{:3d}. {:30s} ({:1.5f})".format(i+1, lfw, distance))
    print(time() - t)

    face.stop()