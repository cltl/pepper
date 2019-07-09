from pepper.framework.abstract.motion import AbstractMotion
from pepper.framework.util import spherical2cartesian

import numpy as np


class NAOqiMotion(AbstractMotion):

    SERVICE = "ALMotion"
    HEAD = ["HeadYaw", "HeadPitch"]

    def __init__(self, session):
        self._service = session.service(NAOqiMotion.SERVICE)
        self._tracker = session.service("ALTracker")

    def look(self, direction, speed=3):
        raise NotImplementedError()

        if len(direction) == 2:
            yaw, pitch = direction
            yaw, pitch = [float(-yaw), float(pitch - np.pi/2)]

            self._service.angleInterpolation(NAOqiMotion.HEAD, [yaw, pitch], [speed, speed], True)

    def point(self, direction):
        raise NotImplementedError()

        coordinates = [float(coordinate) for coordinate in spherical2cartesian(-direction[0], direction[1] - np.pi/2, 2)]
        coordinates = [coordinates[0], coordinates[2], -coordinates[1]]

        print(direction, coordinates)

        LR = "L" if coordinates[1] > 0 else "R"

        self._tracker.pointAt("{}Arm".format(LR), coordinates, 0, 1)
        self._service.openHand("{}Hand".format(LR))
