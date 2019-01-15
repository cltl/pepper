from pepper.framework.backend.naoqi import NAOqiBackend
from pepper.framework import AbstractApplication, FaceDetectionComponent, ObjectDetectionComponent
from pepper import config

from naoqi import ALProxy

from math import sin, cos, pi
from time import sleep


class TrackApplication(AbstractApplication, FaceDetectionComponent, ObjectDetectionComponent):

    TARGET = "Bram"

    def __init__(self, backend):
        super(TrackApplication, self).__init__(backend)

        self._video = ALProxy("ALVideoDevice", config.NAOQI_IP, config.NAOQI_PORT)
        self._motion = ALProxy("ALMotion", config.NAOQI_IP, config.NAOQI_PORT)

        # Get Control over Robot Movement
        ALProxy("ALBasicAwareness", config.NAOQI_IP, config.NAOQI_PORT).setEnabled(True)
        self._motion.setStiffnesses("Head", 1.0)
        exit()

    def on_face(self, faces):
        phi, theta = self._video.getAngularPositionFromImagePosition(0, faces[0].bounds.center)
        self.look(phi, theta)

    def on_object(self, image, objects):
        closest_human = None
        closest_human_area = 0.0

        for obj in objects:
            if obj.name == "person" and obj.bounds.area > closest_human_area:
                closest_human = obj
                closest_human_area = obj.bounds.area

        if closest_human:
            x = closest_human.bounds.x0 + closest_human.bounds.width / 2
            y = closest_human.bounds.y0 + closest_human.bounds.height / 4
            phi, theta = self._video.getAngularPositionFromImagePosition(0, (x, y))
            self.look(phi, theta)

    def reset(self):
        self._motion.setAngles("HeadYaw", 0, 0.2)
        self._motion.setAngles("HeadPitch", 0, 0.2)

    def look(self, phi, theta, speed=0.75):
        speed_phi = min(0.99, speed * abs(phi) ** 2)
        speed_theta = min(0.99, speed * abs(theta) ** 2)

        self._motion.changeAngles("HeadYaw", phi, speed_phi)
        self._motion.changeAngles("HeadPitch", theta, speed_theta)


if __name__ == '__main__':
    TrackApplication(NAOqiBackend()).run()
