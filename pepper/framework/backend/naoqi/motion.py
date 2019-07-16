from pepper.framework.abstract.motion import AbstractMotion
from pepper.framework.util import spherical2cartesian

import qi

import numpy as np

from threading import Thread
from Queue import Queue

from typing import Tuple


class NAOqiMotion(AbstractMotion):
    """
    Connect with NAOqi Motion

    Parameters
    ----------
    session: qi.Session
    """

    SERVICE_MOTION = "ALMotion"
    SERVICE_TRACKER = "ALTracker"
    COMMAND_LIMIT = 1
    FRAME = 0  # 0 = With Respect to Torso

    def __init__(self, session):
        # type: (qi.Session) -> None

        # Connect to Motion and Tracker Services
        self._motion = session.service(NAOqiMotion.SERVICE_MOTION)
        self._tracker = session.service(NAOqiMotion.SERVICE_TRACKER)

        # Create Thread and Queue for 'look' commands
        self._look_queue = Queue()
        self._look_thread = Thread(target=self._look_worker, name="NAOqiLookThread")
        self._look_thread.daemon = True
        self._look_thread.start()

        # Create Thread and Queue for 'point' commands
        self._point_queue = Queue()
        self._point_thread = Thread(target=self._point_worker, name="NAOqiPointThread")
        self._point_thread.daemon = True
        self._point_thread.start()

    def look(self, direction, speed=1):
        # type: (Tuple[float, float], float) -> None
        """
        Look at particular direction

        Parameters
        ----------
        direction: float
        speed: float
        """
        if self._look_queue.qsize() <= NAOqiMotion.COMMAND_LIMIT:
            self._look_queue.put((direction, speed))

    def point(self, direction, speed=1):
        # type: (Tuple[float, float], float) -> None
        """
        Point at particular direction

        Parameters
        ----------
        direction: float
        speed: float
        """
        if self._point_queue.qsize() <= NAOqiMotion.COMMAND_LIMIT:
            self._point_queue.put((direction, speed))

    def _look(self, direction, speed=1):

        # Translate direction to xyz and look at that xyz
        self._tracker.lookAt(self._dir2xyz(direction), NAOqiMotion.FRAME, float(np.clip(speed, 0, 1)), False)

    def _point(self, direction, speed=1):

        # Translate direction to xyz
        coordinates = self._dir2xyz(direction)

        # Point with Left/Right arm to Left/Right targets
        lr = "L" if coordinates[1] > 0 else "R"

        # point higher... (seems hacky)
        coordinates[2] += 1

        # Point with correct arm to target
        self._tracker.pointAt("{}Arm".format(lr), coordinates, NAOqiMotion.FRAME, float(np.clip(speed, 0, 1)))

        # Open hand to 'point' very convincingly
        self._motion.openHand("{}Hand".format(lr))

        # Keep arm pointed at object a little longer
        self._tracker.pointAt("{}Arm".format(lr), coordinates, NAOqiMotion.FRAME, float(np.clip(speed, 0, 1)))

    def _dir2xyz(self, direction):
        x, z, y = spherical2cartesian(-direction[0], direction[1], 5)
        return [float(x), float(y), float(z)]

    def _look_worker(self):
        while True:
            self._look(*self._look_queue.get())

    def _point_worker(self):
        while True:
            self._point(*self._point_queue.get())