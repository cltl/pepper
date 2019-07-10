from pepper.framework.abstract.motion import AbstractMotion
from pepper.framework.util import spherical2cartesian

import numpy as np

from threading import Thread
from Queue import Queue


class NAOqiMotion(AbstractMotion):

    SERVICE_MOTION = "ALMotion"
    SERVICE_TRACKER = "ALTracker"
    COMMAND_LIMIT = 1
    FRAME = 0  # With Respect to Torso

    def __init__(self, session):
        self._motion = session.service(NAOqiMotion.SERVICE_MOTION)
        self._tracker = session.service(NAOqiMotion.SERVICE_TRACKER)

        self._look_queue = Queue()
        self._look_thread = Thread(target=self._look_worker, name="NAOqiLookThread")
        self._look_thread.daemon = True
        self._look_thread.start()

        self._point_queue = Queue()
        self._point_thread = Thread(target=self._point_worker, name="NAOqiPointThread")
        self._point_thread.daemon = True
        self._point_thread.start()

    def look(self, direction, speed=1):
        if self._look_queue.qsize() <= NAOqiMotion.COMMAND_LIMIT:
            self._look_queue.put((direction, speed))

    def point(self, direction, speed=1):
        if self._point_queue.qsize() <= NAOqiMotion.COMMAND_LIMIT:
            self._point_queue.put((direction, speed))

    def _look(self, direction, speed=1):
        self._tracker.lookAt(self._dir2xyz(direction), NAOqiMotion.FRAME, float(np.clip(speed, 0, 1)), False)

    def _point(self, direction, speed=1):
        coordinates = self._dir2xyz(direction)

        LR = "L" if coordinates[1] > 0 else "R"

        coordinates[2] += 1

        self._tracker.pointAt("{}Arm".format(LR), coordinates, NAOqiMotion.FRAME, float(np.clip(speed, 0, 1)))
        self._motion.openHand("{}Hand".format(LR))
        self._tracker.pointAt("{}Arm".format(LR), coordinates, NAOqiMotion.FRAME, float(np.clip(speed, 0, 1)))

    def _dir2xyz(self, direction):
        x, z, y = spherical2cartesian(-direction[0], direction[1], 5)
        return [float(x), float(y), float(z)]

    def _look_worker(self):
        while True:
            self._look(*self._look_queue.get())

    def _point_worker(self):
        while True:
            self._point(*self._point_queue.get())