from pepper.framework.abstract import AbstractCamera, AbstractImage
from pepper.framework.util import Scheduler, Bounds
from pepper import CameraResolution

import numpy as np
import cv2

from time import time, sleep
from typing import List, Callable


class SystemImage(AbstractImage):
    """
    System Image Container

    Since Web Cams generally do not have depth sensors, we set every pixel at a depth of one meter.

    Parameters
    ----------
    image: np.ndarray
        RGB Image (height, width, 3) as Numpy Array
    bounds: Bounds
        Image Bounds (View Space) in Spherical Coordinates (Phi, Theta)
    """

    def __init__(self, image, bounds):
        super(SystemImage, self).__init__(image, bounds, np.ones(image.shape[:2], np.float32))


class SystemCamera(AbstractCamera):
    """
    System Camera

    Parameters
    ----------
    resolution: pepper.framework.CameraResolution
    rate: int
    event_bus: EventBus
    index: int
    """
    def __init__(self, resolution, rate, event_bus, index=0):
        # type: (CameraResolution, int, EventBus, int) -> None
        super(SystemCamera, self).__init__(resolution, rate, event_bus)

        # Get Camera and request resolution
        self._camera = cv2.VideoCapture(index)

    def start(self):
        if not self.resolution == CameraResolution.NATIVE:
            self._camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self._camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        # Check if camera is working
        if not self._camera.isOpened():
            raise RuntimeError("{} could not be opened".format(self.__class__.__name__))

        # Run Image acquisition in Thread
        self._scheduler = Scheduler(self._run, name="SystemCameraThread")
        self._scheduler.start()

        super(SystemCamera, self).start()

        self._log.debug("Started SystemCamera")

    def stop(self):
        super(SystemCamera, self).stop()
        self._scheduler.stop()

    def _run(self):
        t0 = time()

        # Get frame from camera
        # Sometimes the camera fails on the first image. We introduce a three trial policy to initialize the camera
        status = False
        image = None
        for chance in range(3):
            status, image = self._camera.read()
            if status:
                break

        if status:
            if self._running:
                # Resize Image and Convert to RGB
                image = cv2.resize(image, (self.width, self.height))
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                # Call On Image Event
                self.on_image(SystemImage(image, Bounds(-0.55, -0.41+np.pi/2, 0.55, 0.41+np.pi/2)))
        else:
            self._camera.release()
            raise RuntimeError("{} could not fetch image".format(self.__class__.__name__))

        # Maintain frame rate
        sleep(max(0, 1. / self.rate - (time() - t0)))
