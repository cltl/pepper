import os
import socket
import subprocess
from time import sleep

import numpy as np

from pepper import logger
from pepper.framework.util import Bounds
from .api import FaceDetector


class OpenFace(FaceDetector):
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
