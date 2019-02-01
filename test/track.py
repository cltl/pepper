from pepper.framework.backend.naoqi import NAOqiBackend
from pepper.framework import *
from pepper import config

from naoqi import ALProxy
from collections import deque

import numpy as np

import random
from time import time


class TrackApplication(AbstractApplication, TextToSpeechComponent, DisplayComponent, FaceDetectionComponent, ObjectDetectionComponent, StreamedSpeechRecognitionComponent, CameraComponent, MicrophoneComponent):

    TARGET = "Bram"

    def __init__(self, backend):
        super(TrackApplication, self).__init__(backend)
        self._last_person = time()

        self._video = ALProxy("ALVideoDevice", config.NAOQI_IP, config.NAOQI_PORT)
        self._motion = ALProxy("ALMotion", config.NAOQI_IP, config.NAOQI_PORT)
        self._motion.setStiffnesses("Head", 1.0)

        # Get Control over Robot Movement
        self._awareness = ALProxy("ALBasicAwareness", config.NAOQI_IP, config.NAOQI_PORT)
        self._awareness.setEngagementMode("FullyEngaged")
        self._awareness.setStimulusDetectionEnabled("People", False)
        self._awareness.setStimulusDetectionEnabled("Movement", False)
        self._awareness.setEnabled(True)


    def on_image(self, image):
        if time() - self._last_person > 3:
            self.random_look()

            self._last_person = time()
            self._awareness.setEnabled(True)

    def on_object(self, image, objects):
        people = [obj for obj in objects if obj.name == "person"]

        if people:

            self._last_person = time()
            self._awareness.setEnabled(False)

            x = np.average([p.bounds.x0 + p.bounds.width / 2 for p in people], weights=[p.bounds.area for p in people])
            y = np.average([p.bounds.y0 + p.bounds.height / 4 for p in people], weights=[p.bounds.area for p in people])
            self.look(x, y)

    def reset(self):
        self._motion.setAngles("HeadYaw", 0, 0.1)
        self._motion.setAngles("HeadPitch", 0, 0.1)

    def random_look(self, speed=0.05):
        self._motion.setAngles("HeadYaw", random.uniform(-2.0857, 2.0857), speed)
        self._motion.setAngles("HeadPitch", random.uniform(-0.7068, 0.6371), speed)

    def look(self, x, y, speed=1, speed_min=0.02, speed_max=0.3):
        phi, theta = self._video.getAngularPositionFromImagePosition(0, (x, y))

        speed_phi = max(1E-6, min(speed_max, speed * phi ** 2))
        speed_theta = max(1E-6, min(speed_max, speed * theta ** 2))

        if max(speed_phi, speed_theta) > speed_min:
            self._motion.changeAngles("HeadYaw", phi, speed_phi)
            self._motion.changeAngles("HeadPitch", theta, speed_theta)


if __name__ == '__main__':
    TrackApplication(NAOqiBackend()).run()
