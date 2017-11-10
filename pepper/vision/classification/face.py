import subprocess
import os
from PIL import Image
import numpy as np
import json
from time import time


class Face:

    DOCKER_IMAGE = "bamos/openface"
    DOCKER_WORKING_DIRECTORY = "/root/openface"
    DOCKER_NAME = "openface"
    PYTHON_SCRIPT_NAME = 'represent.py'
    PYTHON_SCRIPT_PATH = os.path.join(os.path.dirname(__file__), PYTHON_SCRIPT_NAME)

    TMP = os.path.join(os.path.dirname(__file__), 'tmp.jpg')

    def __init__(self):
        subprocess.call(['docker', 'run',
                         '-d',
                         '-w', self.DOCKER_WORKING_DIRECTORY,
                         '--rm',
                         '--name', self.DOCKER_NAME,
                         self.DOCKER_IMAGE])

        subprocess.call(['docker', 'cp', self.PYTHON_SCRIPT_PATH, "{}:/root/openface".format(self.DOCKER_NAME)])

    def represent(self, image):
        """
        Parameters
        ----------
        image: PIL.Image.Image
        """

        image.save(self.TMP)


        subprocess.call(['docker', 'cp', self.TMP, "{}:/root/openface".format(self.DOCKER_NAME)])
        representation = subprocess.check_output(['docker', 'exec', self.DOCKER_NAME,
                                                  'python', "./{}".format(self.PYTHON_SCRIPT_NAME), 'tmp.jpg'])
        return np.array(json.loads(representation), np.float32)

    def stop(self):
        subprocess.call(['docker', 'stop', self.DOCKER_NAME])




face = Face()

IMAGE_PATH1 = r"C:\Users\Bram\Documents\Pepper\data\lfw\James_Young\James_Young_0001.jpg"
IMAGE_PATH2 = r"C:\Users\Bram\Documents\Pepper\data\lfw\Alan_Ball\Alan_Ball_0001.jpg"
IMAGE_PATH3 = r"C:\Users\Bram\Documents\Pepper\data\lfw\Alan_Ball\Alan_Ball_0002.jpg"

t = time()
delta = face.represent(Image.open(IMAGE_PATH3)) - face.represent(Image.open(IMAGE_PATH1))
print(np.dot(delta, delta), time() - t)

face.stop()