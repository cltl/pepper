import numpy as np

import subprocess
import socket
import os

from time import sleep


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

    SCRIPT_NAME = 'represent.py'
    SCRIPT_PATH = os.path.join(os.path.dirname(__file__), 'openface', SCRIPT_NAME)

    HOST, PORT = '127.0.0.1', 8988

    def __init__(self):
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
        sleep(5)  # Wait for Server to Boot

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


class GenderClassifyClient(object):

    BUFFER_SIZE = 4096

    def __init__(self, address = ('localhost', 8678)):
        """
        Classify Gender From OpenFace Face Representations

        Requires Running the GenderClassifyServer in the pepper_tensorflow repository

        Parameters
        ----------
        address: (str, int)
            Tuple of (<host>, <port>), where server is located
        """
        self.address = address

    def classify(self, face):
        """
        Classify Face(s)

        Parameters
        ----------
        face: np.ndarray
            OpenFace 128D Face Vector(s)

        Returns
        -------
        classification: np.ndarray
            One float per face, indicating P("Female") == 1 - P("Male")
        """
        s = socket.socket()
        s.connect(self.address)
        s.sendall(np.int32(face.nbytes))
        s.send(face)

        response_length = np.frombuffer(s.recv(4), np.int32)
        response_buffer = bytearray()
        while len(response_buffer) < response_length:
            response_buffer.extend(s.recv(self.BUFFER_SIZE))
        return np.frombuffer(response_buffer, np.float32)


if __name__ == "__main__":
    client = GenderClassifyClient()

    PATH = r"C:\Users\Bram\Documents\Pepper\pepper\pepper\vision\classification\data\face_matrix.bin"
    FACE = np.fromfile(PATH, np.float32).reshape(-1, 128)

    print(client.classify(FACE))